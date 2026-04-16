import { useEffect, useState, useCallback } from 'react';
import { Platform } from 'react-native';

// RevenueCat product identifiers
export const PRODUCT_IDS = {
  WEEKLY: 'weekly_99',
  MONTHLY: 'monthly_199',
};

export const ENTITLEMENT_ID = 'pro';

interface RCPackage {
  identifier: string;
  productId: string;
  priceString: string;
  title: string;
}

interface UseRevenueCatReturn {
  isReady: boolean;
  packages: RCPackage[];
  isPremium: boolean;
  purchasing: boolean;
  error: string | null;
  purchase: (packageId: string) => Promise<boolean>;
  restore: () => Promise<boolean>;
  checkEntitlement: () => Promise<boolean>;
}

let Purchases: any = null;
let rcInitialized = false;

// Lazy load RevenueCat — only available on native platforms
async function initRC(): Promise<boolean> {
  if (rcInitialized) return true;
  if (Platform.OS === 'web') return false;

  try {
    const mod = await import('react-native-purchases');
    Purchases = mod.default;

    const apiKey = process.env.EXPO_PUBLIC_RC_API_KEY;
    if (!apiKey) {
      console.warn('[RevenueCat] No API key found');
      return false;
    }

    Purchases.setLogLevel(mod.LOG_LEVEL.VERBOSE);
    Purchases.configure({ apiKey });
    rcInitialized = true;
    console.log('[RevenueCat] Initialized successfully');
    return true;
  } catch (e) {
    console.warn('[RevenueCat] Not available on this platform:', e);
    return false;
  }
}

export function useRevenueCat(): UseRevenueCatReturn {
  const [isReady, setIsReady] = useState(false);
  const [packages, setPackages] = useState<RCPackage[]>([]);
  const [isPremium, setIsPremium] = useState(false);
  const [purchasing, setPurchasing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const setup = async () => {
      const ok = await initRC();
      if (!ok || !mounted) {
        if (mounted) setIsReady(false);
        return;
      }

      try {
        // Fetch offerings
        const offerings = await Purchases.getOfferings();
        if (offerings?.current?.availablePackages && mounted) {
          const pkgs: RCPackage[] = offerings.current.availablePackages.map((p: any) => ({
            identifier: p.identifier,
            productId: p.product?.identifier || p.identifier,
            priceString: p.product?.priceString || '',
            title: p.product?.title || p.identifier,
          }));
          setPackages(pkgs);
        }

        // Check entitlement
        const customerInfo = await Purchases.getCustomerInfo();
        if (mounted) {
          const active = customerInfo?.entitlements?.active?.[ENTITLEMENT_ID];
          setIsPremium(!!active?.isActive);
          setIsReady(true);
        }
      } catch (e: any) {
        console.warn('[RevenueCat] Setup error:', e.message);
        if (mounted) setIsReady(true); // Still mark ready so UI doesn't hang
      }
    };

    setup();
    return () => { mounted = false; };
  }, []);

  const purchase = useCallback(async (packageId: string): Promise<boolean> => {
    if (!Purchases || !rcInitialized) {
      setError('Betaling er ikke tilgjengelig i nettleseren. Bruk appen på mobilen.');
      return false;
    }

    setPurchasing(true);
    setError(null);

    try {
      const offerings = await Purchases.getOfferings();
      const pkg = offerings?.current?.availablePackages?.find(
        (p: any) => p.identifier === packageId || p.product?.identifier === packageId
      );

      if (!pkg) {
        setError('Produktet ble ikke funnet. Prøv igjen.');
        setPurchasing(false);
        return false;
      }

      const { customerInfo } = await Purchases.purchasePackage(pkg);
      const active = customerInfo?.entitlements?.active?.[ENTITLEMENT_ID];

      if (active?.isActive) {
        setIsPremium(true);
        setPurchasing(false);
        return true;
      } else {
        setError('Kjøpet gikk gjennom, men tilgangen ble ikke aktivert. Prøv "Gjenopprett kjøp".');
        setPurchasing(false);
        return false;
      }
    } catch (e: any) {
      if (e.userCancelled) {
        // User cancelled — not an error
        setPurchasing(false);
        return false;
      }
      setError(e.message || 'Noe gikk galt med betalingen');
      setPurchasing(false);
      return false;
    }
  }, []);

  const restore = useCallback(async (): Promise<boolean> => {
    if (!Purchases || !rcInitialized) {
      setError('Gjenoppretting er ikke tilgjengelig i nettleseren.');
      return false;
    }

    setPurchasing(true);
    setError(null);

    try {
      const customerInfo = await Purchases.restorePurchases();
      const active = customerInfo?.entitlements?.active?.[ENTITLEMENT_ID];

      if (active?.isActive) {
        setIsPremium(true);
        setPurchasing(false);
        return true;
      } else {
        setError('Ingen tidligere kjøp funnet.');
        setPurchasing(false);
        return false;
      }
    } catch (e: any) {
      setError(e.message || 'Gjenoppretting feilet');
      setPurchasing(false);
      return false;
    }
  }, []);

  const checkEntitlement = useCallback(async (): Promise<boolean> => {
    if (!Purchases || !rcInitialized) return false;

    try {
      const customerInfo = await Purchases.getCustomerInfo();
      const active = customerInfo?.entitlements?.active?.[ENTITLEMENT_ID];
      const hasPremium = !!active?.isActive;
      setIsPremium(hasPremium);
      return hasPremium;
    } catch {
      return false;
    }
  }, []);

  return { isReady, packages, isPremium, purchasing, error, purchase, restore, checkEntitlement };
}

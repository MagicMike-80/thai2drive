import { useEffect, useState, useCallback } from 'react';
import { Platform } from 'react-native';

// RevenueCat product identifiers — must match RevenueCat dashboard
export const PRODUCT_IDS = {
  MONTHLY: 'monthly_199',
  THREE_MONTH: 'threemonth_399',
  LIFETIME: 'lifetime_699',
};

export const ENTITLEMENT_ID = 'pro';

export interface RCPackage {
  identifier: string;       // e.g. "$rc_weekly", "$rc_monthly"
  productId: string;        // e.g. "weekly_99", "monthly_199"
  priceString: string;
  title: string;
  _raw: any;                // raw package for purchasePackage()
}

interface UseRevenueCatReturn {
  isAvailable: boolean;     // true on native after init
  packages: RCPackage[];
  isPremium: boolean;
  purchasing: boolean;
  error: string | null;
  clearError: () => void;
  purchase: (productId: string) => Promise<boolean>;
  restore: () => Promise<boolean>;
  checkEntitlement: () => Promise<boolean>;
}

let Purchases: any = null;
let rcInitialized = false;

async function initRC(): Promise<boolean> {
  if (rcInitialized) return true;
  if (Platform.OS === 'web') return false;

  try {
    const mod = await import('react-native-purchases');
    Purchases = mod.default;

    const apiKey = process.env.EXPO_PUBLIC_RC_API_KEY;
    if (!apiKey) {
      console.warn('[RC] No API key');
      return false;
    }

    Purchases.setLogLevel(mod.LOG_LEVEL.VERBOSE);
    Purchases.configure({ apiKey });
    rcInitialized = true;
    console.log('[RC] Initialized');
    return true;
  } catch (e) {
    console.warn('[RC] Not available:', e);
    return false;
  }
}

export function useRevenueCat(): UseRevenueCatReturn {
  const [isAvailable, setIsAvailable] = useState(false);
  const [packages, setPackages] = useState<RCPackage[]>([]);
  const [isPremium, setIsPremium] = useState(false);
  const [purchasing, setPurchasing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;

    (async () => {
      const ok = await initRC();
      if (!ok || !alive) return;

      try {
        // Load offerings → packages
        const offerings = await Purchases.getOfferings();
        if (offerings?.current?.availablePackages && alive) {
          setPackages(
            offerings.current.availablePackages.map((p: any) => ({
              identifier: p.identifier,
              productId: p.product?.identifier || p.identifier,
              priceString: p.product?.priceString || '',
              title: p.product?.title || p.identifier,
              _raw: p,
            }))
          );
        }

        // Check current entitlement
        const info = await Purchases.getCustomerInfo();
        if (alive) {
          setIsPremium(!!info?.entitlements?.active?.[ENTITLEMENT_ID]?.isActive);
          setIsAvailable(true);
        }
      } catch (e: any) {
        console.warn('[RC] Setup:', e.message);
        if (alive) setIsAvailable(true);
      }
    })();

    // Listen for subscription changes
    let unsub: any;
    if (Purchases && rcInitialized) {
      unsub = Purchases.addCustomerInfoUpdateListener((info: any) => {
        setIsPremium(!!info?.entitlements?.active?.[ENTITLEMENT_ID]?.isActive);
      });
    }

    return () => { alive = false; unsub?.remove?.(); };
  }, []);

  const clearError = useCallback(() => setError(null), []);

  // Purchase a package by product ID (e.g. "weekly_99")
  const purchase = useCallback(async (productId: string): Promise<boolean> => {
    if (!Purchases || !rcInitialized) {
      setError('Betaling krever mobilappen. Ikke tilgjengelig i nettleseren.');
      return false;
    }

    setPurchasing(true);
    setError(null);

    try {
      // Find matching package from loaded offerings
      const offerings = await Purchases.getOfferings();
      const allPkgs = offerings?.current?.availablePackages || [];

      const pkg = allPkgs.find(
        (p: any) => p.product?.identifier === productId || p.identifier === productId
      );

      if (!pkg) {
        setError('Produktet ble ikke funnet. Sjekk RevenueCat-oppsettet.');
        setPurchasing(false);
        return false;
      }

      const { customerInfo } = await Purchases.purchasePackage(pkg);
      const active = !!customerInfo?.entitlements?.active?.[ENTITLEMENT_ID]?.isActive;

      if (active) {
        setIsPremium(true);
        setPurchasing(false);
        return true;
      }

      setError('Kjøpet fullførte, men tilgang ble ikke aktivert. Prøv "Gjenopprett kjøp".');
      setPurchasing(false);
      return false;
    } catch (e: any) {
      setPurchasing(false);
      if (e.userCancelled) return false;
      setError(e.message || 'Betalingsfeil');
      return false;
    }
  }, []);

  const restore = useCallback(async (): Promise<boolean> => {
    if (!Purchases || !rcInitialized) {
      setError('Gjenoppretting krever mobilappen.');
      return false;
    }

    setPurchasing(true);
    setError(null);

    try {
      const info = await Purchases.restorePurchases();
      const active = !!info?.entitlements?.active?.[ENTITLEMENT_ID]?.isActive;
      setIsPremium(active);
      setPurchasing(false);

      if (!active) setError('Ingen tidligere kjøp funnet.');
      return active;
    } catch (e: any) {
      setError(e.message || 'Gjenoppretting feilet');
      setPurchasing(false);
      return false;
    }
  }, []);

  const checkEntitlement = useCallback(async (): Promise<boolean> => {
    if (!Purchases || !rcInitialized) return false;
    try {
      const info = await Purchases.getCustomerInfo();
      const active = !!info?.entitlements?.active?.[ENTITLEMENT_ID]?.isActive;
      setIsPremium(active);
      return active;
    } catch { return false; }
  }, []);

  return { isAvailable, packages, isPremium, purchasing, error, clearError, purchase, restore, checkEntitlement };
}

# Prompt 2 — Strategisk gap-analyse

Brukes **før** noe bygges. Tvinger Claude til å analysere instruksjonen din som
strateg i stedet for å begynne å produsere på en uklar idé.

Dette er den viktigste av de tre promptene. Et par minutter her sparer deg for
fire dokumenter bygget på feil premiss.

## Originalen (ordrett fra kilden)

> Before you build analyze my instructions like a strategist tell me what I am
> clearly asking for what is implied but stated what important context is missing
> what decisions I need to make before you build

## Norsk versjon

> Før du bygger noe: analyser instruksjonen min som en strateg. Fortell meg
> 1) hva jeg tydelig ber om, 2) hva som er underforstått men ikke sagt,
> 3) hvilken viktig kontekst som mangler, og 4) hvilke beslutninger jeg må ta
> før du kan bygge. Ikke begynn å bygge før jeg har svart.

## Formatet du skal få tilbake

```markdown
### 1. Hva du tydelig ber om
### 2. Hva som er underforstått
### 3. Viktig kontekst som mangler
### 4. Beslutninger du må ta før vi bygger
```

Siste seksjon skal være **spørsmål du kan svare på**, ikke observasjoner.
«Målgruppen er uklar» er ubrukelig. «Starter vi med eleven som har strøket én
gang, eller den som ikke har prøvd ennå?» er noe du kan ta stilling til.

## Regel

Er svaret på et av spørsmålene i seksjon 4 «vet ikke» — det er da
market-signal-researcher skal kjøres. Ikke gjett deg videre.

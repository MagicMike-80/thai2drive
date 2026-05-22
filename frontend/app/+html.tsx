// @ts-nocheck
import { ScrollViewStyleReset } from "expo-router/html";
import type { PropsWithChildren } from "react";

export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="en" style={{ height: "100%" }}>
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />
        {/*
          Disable body scrolling on web to make ScrollView components work correctly.
          If you want to enable scrolling, remove `ScrollViewStyleReset` and
          set `overflow: auto` on the body style below.
        */}
        <ScrollViewStyleReset />
        <style
          dangerouslySetInnerHTML={{
            __html: `
              body > div:first-child { position: fixed !important; top: 0; left: 0; right: 0; bottom: 0; }
              [role="tablist"] [role="tab"] * { overflow: visible !important; }
              [role="heading"], [role="heading"] * { overflow: visible !important; }

              /*
               * ── Mobile-app scrollbar suppression ─────────────────────────
               * Hiding scrollbars is intentional here: the web shell wraps
               * the app in a phone-frame silhouette, and native mobile apps
               * never show scrollbars. Scrolling (wheel, trackpad, touch)
               * still works — only the visual track is removed.
               *
               * WebKit/Blink (Chrome, Safari, Edge):
               */
              *::-webkit-scrollbar          { display: none; }
              *::-webkit-scrollbar-track    { background: transparent; }
              *::-webkit-scrollbar-thumb    { background: transparent; }

              /* Firefox */
              * { scrollbar-width: none; }

              /* IE / legacy Edge */
              * { -ms-overflow-style: none; }

              /*
               * ── Prevent text/element selection on interactive surfaces ────
               * Mobile apps suppress tap-selection; this matches that feel.
               * Input fields keep selection enabled (user-select: auto below).
               */
              body { -webkit-user-select: none; user-select: none; }
              input, textarea, [contenteditable] {
                -webkit-user-select: text;
                user-select: text;
              }
            `,
          }}
        />
      </head>
      <body
        style={{
          margin: 0,
          height: "100%",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {children}
      </body>
    </html>
  );
}

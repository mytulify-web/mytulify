/** Privacy-conscious GA4 events: never pass user-entered content or results. */

type AnalyticsEventParams = Record<string, string | number | boolean>;

declare global {
  interface Window {
    gtag?: (
      command: "event",
      eventName: string,
      params?: AnalyticsEventParams,
    ) => void;
  }
}

export function trackAnalyticsEvent(
  eventName: string,
  params: AnalyticsEventParams = {},
): void {
  if (typeof window === "undefined" || typeof window.gtag !== "function") return;
  window.gtag("event", eventName, params);
}

/** Privacy-conscious GA4 events: never pass user-entered content or results. */

type AnalyticsEventParams = Record<string, string | number | boolean>;
type GtagWindow = Window & {
  gtag?: (
    command: "event",
    eventName: string,
    params?: AnalyticsEventParams,
  ) => void;
};

export function trackAnalyticsEvent(
  eventName: string,
  params: AnalyticsEventParams = {},
): void {
  if (typeof window === "undefined") return;
  const gtag = (window as GtagWindow).gtag;
  if (typeof gtag !== "function") return;
  gtag("event", eventName, params);
}

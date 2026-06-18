import { create } from 'zustand';
import { fetchSubscriptionEntitlements } from '../api/subscriptions';
import { resolveTariffLimits } from '../utils/constants';

const useSubscriptionStore = create((set, get) => ({
  entitlementsPayload: null,
  limits: resolveTariffLimits('free'),
  isLoading: false,
  error: null,

  loadEntitlements: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const payload = await fetchSubscriptionEntitlements(params);
      set({
        entitlementsPayload: payload,
        limits: resolveTariffLimits(payload.plan, payload),
        isLoading: false,
      });
      return payload;
    } catch (error) {
      set({ error, isLoading: false });
      throw error;
    }
  },

  hasFeature: (feature) => {
    const payload = get().entitlementsPayload;
    const entitlement = payload?.entitlements?.find(
      (item) => item.feature === feature,
    );
    return Boolean(entitlement?.allowed);
  },
}));

export default useSubscriptionStore;

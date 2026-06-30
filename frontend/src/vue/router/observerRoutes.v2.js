/** Observer portal routes — excluded from v1.0 (Phase 32.1). Re-enable in a future release. */

export const observerRoutesV2 = [
  {
    path: "/observe",
    component: () => import("@/layouts/ObserverLayout.vue"),
    meta: { public: true },
    children: [
      {
        path: "",
        name: "observer",
        component: () => import("@/views/public/ObserverPortalView.vue"),
        meta: { title: "Election Observer Portal", public: true },
      },
    ],
  },
];

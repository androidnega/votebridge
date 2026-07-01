<script setup>
import { computed } from "vue";
import { VIcon } from "@/components/ui";
import { formatNotificationCategory, getNotificationVisual } from "@/config/notificationVisuals";
import { formatRelativeTime } from "@/utils/formatTime";

const props = defineProps({
  item: { type: Object, required: true },
  compact: { type: Boolean, default: false },
  showActions: { type: Boolean, default: true },
  archived: { type: Boolean, default: false },
});

const emit = defineEmits(["open", "mark-read", "archive", "delete"]);

const visual = computed(() => getNotificationVisual(props.item.category));
const categoryLabel = computed(() => formatNotificationCategory(props.item.category));
const timeLabel = computed(() => formatRelativeTime(props.item.created_at));

function handleOpen() {
  emit("open", props.item);
  if (!props.item.is_read && !props.archived) {
    emit("mark-read", props.item.uuid);
  }
}
</script>

<template>
  <article
    class="group relative flex items-center gap-3 border-b border-border px-3 py-2 last:border-b-0 sm:px-4"
    :class="[
      compact ? 'min-h-[2.75rem]' : 'min-h-[3rem]',
      item.is_read ? 'bg-white' : 'bg-brand-50/30',
      'transition hover:bg-surface-muted/70',
    ]"
  >
    <button
      type="button"
      class="flex min-w-0 flex-1 items-center gap-3 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
      @click="handleOpen"
    >
      <span class="flex w-2 shrink-0 justify-center" aria-hidden="true">
        <span
          v-if="!item.is_read"
          class="h-1.5 w-1.5 rounded-full bg-brand-600"
        />
      </span>

      <span
        class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border"
        :style="visual.style"
        aria-hidden="true"
      >
        <VIcon :name="visual.icon" size="sm" />
      </span>

      <span class="min-w-0 flex-1">
        <span class="flex items-center gap-2">
          <span
            class="truncate text-sm leading-tight"
            :class="item.is_read ? 'font-medium text-slate-700' : 'font-semibold text-slate-900'"
          >
            {{ item.title }}
          </span>
          <span
            v-if="categoryLabel && !compact"
            class="hidden shrink-0 rounded-full border border-border bg-white px-1.5 py-0.5 text-[10px] font-medium capitalize text-slate-500 sm:inline"
          >
            {{ categoryLabel }}
          </span>
        </span>
        <span
          v-if="item.body && !compact"
          class="mt-0.5 block truncate text-xs leading-snug text-slate-500"
        >
          {{ item.body }}
        </span>
      </span>

      <time
        class="shrink-0 text-[11px] tabular-nums text-slate-400"
        :datetime="item.created_at"
      >
        {{ timeLabel }}
      </time>
    </button>

    <div
      v-if="showActions"
      class="flex shrink-0 items-center gap-0.5 opacity-100 sm:opacity-0 sm:transition sm:group-hover:opacity-100 sm:group-focus-within:opacity-100"
    >
      <button
        v-if="!item.is_read && !archived"
        type="button"
        class="flex h-8 w-8 items-center justify-center rounded-input text-slate-400 transition hover:bg-white hover:text-brand-700"
        aria-label="Mark as read"
        @click.stop="emit('mark-read', item.uuid)"
      >
        <VIcon name="check" size="sm" />
      </button>
      <button
        v-if="!archived"
        type="button"
        class="flex h-8 w-8 items-center justify-center rounded-input text-slate-400 transition hover:bg-white hover:text-slate-700"
        aria-label="Archive notification"
        @click.stop="emit('archive', item.uuid)"
      >
        <VIcon name="archive" size="sm" />
      </button>
      <button
        type="button"
        class="flex h-8 w-8 items-center justify-center rounded-input text-slate-400 transition hover:bg-white hover:text-danger-600"
        aria-label="Delete notification"
        @click.stop="emit('delete', item.uuid)"
      >
        <VIcon name="x" size="sm" />
      </button>
    </div>
  </article>
</template>

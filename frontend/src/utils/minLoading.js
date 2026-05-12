// 最短加载展示时间：避免加载动画“闪一下就消失”
// 仅用于组件内部的 loading/pageLoading 状态切换。

const DEFAULT_MIN_LOADING_MS = 800

function getNowMs() {
  // performance.now 更适合计算耗时；在极少数环境下退回 Date.now
  return (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now()
}

/**
 * 在至少 minMs 毫秒后再把 loadingRef 置为 false。
 * @param {{ value: boolean }} loadingRef Vue ref（如 loading 或 pageLoading）
 * @param {number} startedAtMs 开始时间（建议用 getNowMs()）
 * @param {number} minMs 最短展示时长
 */
export function ensureMinLoadingOff(loadingRef, startedAtMs, minMs = DEFAULT_MIN_LOADING_MS) {
  const elapsed = getNowMs() - startedAtMs
  const remain = Math.max(0, minMs - elapsed)
  if (remain === 0) {
    loadingRef.value = false
    return
  }
  setTimeout(() => {
    loadingRef.value = false
  }, remain)
}

export function getNowMsSafe() {
  return getNowMs()
}

export { DEFAULT_MIN_LOADING_MS }


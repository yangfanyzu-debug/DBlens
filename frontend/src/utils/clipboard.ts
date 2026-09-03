export async function copyTextToClipboard(text: string) {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text)
      return
    } catch {
      // Fall back for pages where Clipboard API is blocked by context.
    }
  }

  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  try {
    textarea.focus()
    textarea.select()
    if (!document.execCommand('copy')) {
      throw new Error('Clipboard copy failed')
    }
  } finally {
    document.body.removeChild(textarea)
  }
}

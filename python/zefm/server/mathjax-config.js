/* Equivalent to mathjaxfilterr's MathJax.Hub.Config(), for MathJax v3.
 * No jQuery, no inline script, and works with ZEFM's sandboxed previews.
 * Must be loaded BEFORE the MathJax component (both scripts use defer).
 */
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    packages: {'[+]': ['ams']}
  },
  svg: {
    fontCache: 'local'
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
  }
};

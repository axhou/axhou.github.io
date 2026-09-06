// Typeset a semester when it opens, so formulas use its visible width.
window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    processEscapes: true
  },
  svg: { fontCache: 'global' },
  startup: {
    typeset: false,
    pageReady() {
      return MathJax.startup.defaultPageReady().then(() => {
        let queue = Promise.resolve();
        const render = semester => {
          if (!semester.open || semester.dataset.mathReady) return;
          semester.dataset.mathReady = 'pending';
          queue = queue.then(async () => {
            if (!semester.open) {
              delete semester.dataset.mathReady;
              return;
            }
            await MathJax.typesetPromise([semester]);
            semester.dataset.mathReady = 'true';
          }).catch(error => {
            delete semester.dataset.mathReady;
            console.error('Unable to typeset seminar formulas:', error);
          });
        };
        document.querySelectorAll('.archive-semester').forEach(semester => {
          semester.addEventListener('toggle', () => render(semester));
          render(semester);
        });
      });
    }
  }
};

// Typeset titles and abstracts when their own disclosure becomes visible.
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
        const render = (element, targets, isVisible) => {
          if (!isVisible() || element.dataset.mathReady) return;
          element.dataset.mathReady = 'pending';
          queue = queue.then(async () => {
            if (!isVisible()) {
              delete element.dataset.mathReady;
              return;
            }
            await MathJax.typesetPromise(targets);
            element.dataset.mathReady = 'true';
          }).catch(error => {
            delete element.dataset.mathReady;
            console.error('Unable to typeset seminar formulas:', error);
          });
        };
        document.querySelectorAll('.archive-semester').forEach(semester => {
          const abstracts = [...semester.querySelectorAll('.abstract-details')];
          const renderAbstract = details => render(
            details, [details], () => semester.open && details.open
          );
          const renderSemester = () => {
            if (!semester.open) return;
            render(semester, [...semester.querySelectorAll('.seminar-heading, .title')], () => semester.open);
            abstracts.forEach(renderAbstract);
          };
          abstracts.forEach(details => {
            details.addEventListener('toggle', () => renderAbstract(details));
          });
          semester.addEventListener('toggle', renderSemester);
          renderSemester();
        });
        document.querySelectorAll('body > .seminar-entry').forEach(entry => {
          render(entry, [...entry.querySelectorAll('.seminar-heading, .title')], () => true);
          const details = entry.querySelector('.abstract-details');
          if (!details) return;
          const renderAbstract = () => render(details, [details], () => details.open);
          details.addEventListener('toggle', renderAbstract);
          renderAbstract();
        });
      });
    }
  }
};

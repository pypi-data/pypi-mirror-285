
const copyToSystem = (clipboardData: string): void => {
     const node = document.body;
     const handler = (event: ClipboardEvent) => {
          const data = event.clipboardData || (window as any).clipboardData;
          data.setData('text', clipboardData);
          event.preventDefault();
          node.removeEventListener('copy', handler);
     };
     node.addEventListener('copy', handler);
     generateEvent(node);
}

/**
 * Generate a clipboard event on a node.
 *
 * @param node - The element on which to generate the event.
 *
 * @param type - The type of event to generate.
 *   `'paste'` events cannot be programmatically generated.
 *
 * #### Notes
 * This can only be called in response to a user input event.
 */
function generateEvent(
     node: HTMLElement,
     type: 'copy' | 'cut' = 'copy'
): void {
     // http://stackoverflow.com/a/5210367

     // Identify selected text.
     let sel = window.getSelection();

     // Save the current selection.
     const savedRanges: any[] = [];
     for (let i = 0, len = sel?.rangeCount || 0; i < len; ++i) {
          savedRanges[i] = sel!.getRangeAt(i).cloneRange();
     }

     // Select the node content.
     const range = document.createRange();
     range.selectNodeContents(node);
     if (sel) {
          sel.removeAllRanges();
          sel.addRange(range);
     }

     // Execute the command.
     document.execCommand(type);

     // Restore the previous selection.
     sel = window.getSelection();
     if (sel) {
          sel.removeAllRanges();
          for (let i = 0, len = savedRanges.length; i < len; ++i) {
               sel.addRange(savedRanges[i]);
          }
     }
}

export default copyToSystem;

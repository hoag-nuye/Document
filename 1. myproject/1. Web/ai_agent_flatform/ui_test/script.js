// --- Tab Navigation (Single-Page) ---
const tabs = document.querySelectorAll('.sidebar__nav li');
const sections = document.querySelectorAll('.tab-content');
const title = document.getElementById('main-title');

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    // 1. Update active class
    tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    // 2. Show corresponding section
    const target = tab.dataset.tab;
    sections.forEach(sec => {
      if (sec.id === target) sec.classList.remove('hidden');
      else sec.classList.add('hidden');
    });

    // 3. Update header title
    title.textContent = tab.textContent;
  });
});

// --- Drag & Drop cho Board Agents ---
const board = document.querySelector('.board');
let currentAgent = null;
let offsetX = 0, offsetY = 0;

board.addEventListener('mousedown', e => {
  // console.log(e)
  if (e.target.classList.contains('agent')) {
    currentAgent = e.target;
    // Tính toán offset để kéo mượt mà
    const rect = currentAgent.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
  }
});

document.addEventListener('mousemove', e => {
  if (currentAgent) {
    // Giới hạn kéo trong board
    const boardRect = board.getBoundingClientRect();
    let x = e.clientX - boardRect.left - offsetX;
    let y = e.clientY - boardRect.top - offsetY;
    // Giới hạn toạ độ
    x = Math.max(0, Math.min(boardRect.width - currentAgent.offsetWidth, x));
    y = Math.max(0, Math.min(boardRect.height - currentAgent.offsetHeight, y));
    currentAgent.style.left = x + 'px';
    currentAgent.style.top  = y + 'px';
  }
});

document.addEventListener('mouseup', () => {
  currentAgent = null;
});

/**
 * DAINIK JAHAN IPTV — MAIN APPLICATION LOGIC
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log('[DJ-IPTV] Platform initialized.');

  // Toast helper
  window.djShowToast = function(msg) {
    let toast = document.getElementById('djGlobalToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'djGlobalToast';
      toast.className = 'dj-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.display = 'flex';
    setTimeout(() => {
      toast.style.display = 'none';
    }, 3200);
  };

  // Search input handler
  const searchInput = document.getElementById('djGlobalSearch');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const cards = document.querySelectorAll('.dj-card');
      cards.forEach(card => {
        const title = card.getAttribute('data-title') || '';
        const cat = card.getAttribute('data-category') || '';
        const lang = card.getAttribute('data-language') || '';
        const country = card.getAttribute('data-country') || '';
        const match = title.includes(q) || cat.includes(q) || lang.includes(q) || country.includes(q);
        card.style.display = match ? 'flex' : 'none';
      });
    });
  }

  // Filter Chips handler
  const filterChips = document.querySelectorAll('.dj-filter-bar .dj-chip');
  if (filterChips.length > 0) {
    filterChips.forEach(chip => {
      chip.addEventListener('click', () => {
        filterChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        const filterVal = chip.getAttribute('data-filter');
        const cards = document.querySelectorAll('.dj-card');
        
        cards.forEach(card => {
          if (filterVal === 'all') {
            card.style.display = 'flex';
          } else if (filterVal === 'bangladesh') {
            card.style.display = card.getAttribute('data-bangladesh') === 'true' ? 'flex' : 'none';
          } else if (filterVal === 'international') {
            card.style.display = card.getAttribute('data-bangladesh') === 'false' ? 'flex' : 'none';
          } else {
            const cat = card.getAttribute('data-category') || '';
            card.style.display = (cat.toLowerCase() === filterVal.toLowerCase()) ? 'flex' : 'none';
          }
        });
      });
    });
  }

  // Channel Card Click handler -> Switch channel in player
  const channelCards = document.querySelectorAll('.dj-card[data-channel-json]');
  channelCards.forEach(card => {
    const playBtn = card.querySelector('.dj-card-play-btn');
    const channelJson = card.getAttribute('data-channel-json');
    if (channelJson && playBtn) {
      try {
        const channelData = JSON.parse(channelJson);
        playBtn.addEventListener('click', (e) => {
          e.preventDefault();
          if (window.djPlayer) {
            window.djPlayer.loadChannel(channelData);
            window.scrollTo({ top: 0, behavior: 'smooth' });
            window.djShowToast(`'${channelData.name}' চালু করা হয়েছে`);
          }
        });
      } catch (e) {
        console.error('Invalid channel JSON on card:', e);
      }
    }
  });

  // Favorite button on cards
  const favBtns = document.querySelectorAll('.dj-icon-btn[data-fav-id]');
  favBtns.forEach(btn => {
    const id = btn.getAttribute('data-fav-id');
    const title = btn.getAttribute('data-fav-title');
    if (window.DainikJahanUser && window.DainikJahanUser.isFavorite('channel', id)) {
      btn.classList.add('active');
      btn.innerHTML = '❤️';
    }
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (window.DainikJahanUser) {
        const isFav = window.DainikJahanUser.toggleFavorite('channel', id, title);
        btn.classList.toggle('active', isFav);
        btn.innerHTML = isFav ? '❤️' : '🤍';
      }
    });
  });

  // Sidebar Channel Click
  const sideItems = document.querySelectorAll('.dj-side-item[data-channel-json]');
  sideItems.forEach(item => {
    item.addEventListener('click', () => {
      sideItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      const channelJson = item.getAttribute('data-channel-json');
      if (channelJson && window.djPlayer) {
        try {
          const data = JSON.parse(channelJson);
          window.djPlayer.loadChannel(data);
          window.djShowToast(`'${data.name}' চালু হয়েছে`);
        } catch (err) {}
      }
    });
  });
});

/* Click-to-play YouTube. Each .yt box holds a link to the video and a local
   thumbnail; nothing is requested from YouTube until the visitor presses play.
   Then the link is swapped for YouTube's privacy-enhanced (no-cookie) player. */
document.querySelectorAll('.yt[data-id]').forEach(function (box) {
  var link = box.querySelector('a');
  if (!link) return;
  link.addEventListener('click', function (e) {
    e.preventDefault();
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(box.dataset.id) + '?autoplay=1&rel=0';
    f.title = box.dataset.title || 'Video';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen = true;
    box.replaceChildren(f);
    f.focus();
  });
});

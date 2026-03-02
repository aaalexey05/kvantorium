(function(){
  function getCookie(name){
    const value = `; ${document.cookie}`.split(`; ${name}=`);
    if (value.length === 2) return value.pop().split(';').shift();
  }
  htmx.on('htmx:configRequest', (event) => {
    const token = getCookie('csrftoken');
    if (token) event.detail.headers['X-CSRFToken'] = token;
  });
})();

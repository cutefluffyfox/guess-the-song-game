var showChatModeration = false;
var showUserModeration = false;

document.onclick = function(e) {  // hide context menu when out of focus
  var chatContextMenu = document.getElementById("chat-context-menu");
  chatContextMenu.style.display = 'none';

  var userContextMenu = document.getElementById("user-context-menu");
  userContextMenu.style.display = 'none';
}

document.oncontextmenu = function(e) {
  var element = e.target

  // process chat message context menu
  if (showChatModeration && element.className.startsWith("message")) {
    var chatContextMenu = document.getElementById("chat-context-menu");

    var blockId = element.id.slice(4);

    e.preventDefault();
    chatContextMenu.style.position = "absolute";
    chatContextMenu.style.left = e.clientX + 'px';
    chatContextMenu.style.top = e.clientY + 'px';
    chatContextMenu.style.display = 'block';

    document.getElementById('chat-delete-single').onclick = function() { delete_message(blockId, false, false); }
    document.getElementById('chat-delete-all').onclick = function() { delete_message(blockId, true, false); }
    document.getElementById('chat-mute-user').onclick = function() { delete_message(blockId, true, true); }
  }
  else if (showUserModeration && element.className.startsWith("username")) {
    var userContextMenu = document.getElementById("user-context-menu");

    var username = element.innerHTML;
    $('#user-context-menu').empty();
    $('#user-context-menu').html('loading...');
    socket.emit('check-permission', {username: username});

//    fetch(location.protocol + '//' + document.domain + ':' + location.port + '/api/v1/' + username + '/permissions').then(function(response) {
//      return response.json();
//    }).then(function(data) { make_user_management_menu(username, data); })

    e.preventDefault();
    userContextMenu.style.position = "absolute";
    userContextMenu.style.left = e.clientX + 'px';
    userContextMenu.style.top = e.clientY + 'px';
    userContextMenu.style.display = 'block';
  }
}

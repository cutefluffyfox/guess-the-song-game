document.onclick = function(e) {  // hide context menu when out of focus
  var chatContextMenu = document.getElementById("chat-context-menu");
  chatContextMenu.style.display = 'none';
}

document.oncontextmenu = function(e) {
  var element = e.target
  // process chat message context menu
  if (element.className.startsWith("message")) {
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

//    chatContextMenu.innerHTML = chatContextMenu.innerHTML;
  }
}

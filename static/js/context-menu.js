var showChatModeration = false;
var showUserModeration = false;


function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

var colorPicker = document.getElementById("username-color-input");
colorPicker.addEventListener("change", watchColorPicker);

function watchColorPicker(event) {
  var newColor = event.target.value;
  change_username_color(newColor);
}


document.onclick = function(e) {  // hide context menu when out of focus
  var chatContextMenu = document.getElementById("chat-context-menu");
  chatContextMenu.style.display = 'none';

  var userContextMenu = document.getElementById("user-context-menu");
  userContextMenu.style.display = 'none';

  var colorSelectionMenu = document.getElementById("color-selection-menu");
  colorSelectionMenu.style.display = 'none';
}

document.oncontextmenu = function(e) {
  var element = e.target

  // process chat message context menu
  if (element.className == "username" && element.innerText == (currentUsername + ': ')) {
    var colorSelectionMenu = document.getElementById("color-selection-menu");

    var usernameColor = element.style.color;  // e.x.: rgb(60, 180, 75)
    var colorVals = usernameColor.slice(4, -1).split(",");
    document.getElementById("username-color-input").value = rgbToHex(parseInt(colorVals[0]), parseInt(colorVals[1]), parseInt(colorVals[2]));

    e.preventDefault();
    colorSelectionMenu.style.position = "absolute";
    colorSelectionMenu.style.left = e.clientX + 'px';
    colorSelectionMenu.style.top = e.clientY + 'px';
    colorSelectionMenu.style.display = 'block';
  }
  else if (showChatModeration && element.className.startsWith("message")) {
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
  else if (showUserModeration && element.className.startsWith("username") || showChatModeration && element.className.startsWith("username")) {
    var userContextMenu = document.getElementById("user-context-menu");

    var username = element.innerHTML;
    $('#user-context-menu').empty();
    $('#user-context-menu').html('loading...');
    socket.emit('check-permission', {username: username});

    e.preventDefault();
    userContextMenu.style.position = "absolute";
    userContextMenu.style.left = e.clientX + 'px';
    userContextMenu.style.top = e.clientY + 'px';
    userContextMenu.style.display = 'block';
  }
}

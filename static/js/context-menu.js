document.onclick = function(e) {  // hide context menu when out of focus
  var chatContextMenu = document.getElementById("chat-context-menu");
  chatContextMenu.style.display = 'none';
}

document.oncontextmenu = function(e) {
  var element = e.target
  // process chat message context menu
  console.log(element)
  if (element.className.startsWith("message")) {
    var chatContextMenu = document.getElementById("chat-context-menu");

    e.preventDefault();
    chatContextMenu.style.position = "absolute";
    chatContextMenu.style.left = e.clientX + 'px';
    chatContextMenu.style.top = e.clientY + 'px';
    chatContextMenu.style.display = 'block';

//    chatContextMenu.innerHTML = chatContextMenu.innerHTML;
  }
}

//
//// context menu for chat
//var rgtClickContextMenu = document.getElementById('chat');
//
//
//document.oncontextmenu = function(e) {
//  alert(e.target.id);
////  var elmnt = e.target
////  if (elmnt.className.startsWith("cls-context-menu")) {
////    e.preventDefault();
////    var eid = elmnt.id.replace(/link-/, "")
////    rgtClickContextMenu.style.left = e.pageX + 'px'
////    rgtClickContextMenu.style.top = e.pageY + 'px'
////    rgtClickContextMenu.style.display = 'block'
////    var toRepl = "to=" + eid.toString()
////    rgtClickContextMenu.innerHTML = rgtClickContextMenu.innerHTML.replace(/to=\d+/g, toRepl)
////    alert(rgtClickContextMenu.innerHTML.toString())
////  }
//  alert(rgtClickContextMenu.innerHTML.toString());
//}
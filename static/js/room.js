var socket;
var canChangeLeaderboard = false;


$(document).ready(function(){
  socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/room');
  socket.on('connect', function() {
      socket.emit('join', {});
  });
  socket.on('disconnect', function(data) {
    socket.emit('left', {});
  });
  socket.on('status', function(data) {
      var shouldScroll = Math.ceil(10 + $('#chat')[0].scrollTop + $('#chat')[0].clientHeight) >= $('#chat')[0].scrollHeight;
      $('#chat').append('<div class="chat-message">' + '&lt;' + data.msg + '&gt;' + '</div>');
      if (shouldScroll) {
          $('#chat').scrollTop($('#chat')[0].scrollHeight);
      }
  });
  socket.on('message', function(data) {
      var shouldScroll = Math.ceil(10 + $('#chat')[0].scrollTop + $('#chat')[0].clientHeight) >= $('#chat')[0].scrollHeight;
      var msg = '<div class="chat-message"><span class="username" style="color: ' + data.color + '">' + data.username + ': </span><span class="message" id="msg_' + data.msg_id + '">' + data.msg + '</span></div>'
      $('#chat').append(msg);
      if (shouldScroll) {
          $('#chat').scrollTop($('#chat')[0].scrollHeight);
      }
  });
  socket.on('show-permissions', function(data) {
      make_user_management_menu(data["username"], data["permissions"]);
  });
  socket.on('user-info', function(data) {
      $('#user-submissions').empty();
      $('#user-submissions').append('<h4 class="h4">~ Your guesses ~</h4>');
      for (const submission of data["submissions"]) {
          if (!submission["processed"]) {
              $('#user-submissions').append('<div class="guess"><div class="guess_number number_unk">?</div><div class="guess_name">' + submission["song"] + '</div><div class="guess_person">' + submission["submitter"] + '</div></div>');
          } else if (submission["score"] < 0.5) {
              $('#user-submissions').append('<div class="guess"><div class="guess_number number_0">' + submission["score"] + '</div><div class="guess_name">' + submission["song"] + '</div><div class="guess_person">' + submission["submitter"] + '</div></div>');
          } else if (submission["score"] < 1.5) {
              $('#user-submissions').append('<div class="guess"><div class="guess_number number_1">' + submission["score"] + '</div><div class="guess_name">' + submission["song"] + '</div><div class="guess_person">' + submission["submitter"] + '</div></div>');
          } else if (submission["score"] < 2.5) {
              $('#user-submissions').append('<div class="guess"><div class="guess_number number_2">' + submission["score"] + '</div><div class="guess_name">' + submission["song"] + '</div><div class="guess_person">' + submission["submitter"] + '</div></div>');
          } else {
              $('#user-submissions').append('<div class="guess"><div class="guess_number number_3">' + submission["score"] + '</div><div class="guess_name">' + submission["song"] + '</div><div class="guess_person">' + submission["submitter"] + '</div></div>');
          }
      }
      var submitBnt = document.getElementById("prediction-submit");
      submitBnt.innerHTML = 'SEND <i>(' + data["submissions-left"] + ' Attempts left)</i>';

      // check permission to chat
      var chatTextArea = document.getElementById("text");
      chatTextArea.disabled = !data["permissions"]["can_chat"];
      if (data["permissions"]["can_chat"]) {
        chatTextArea.placeholder = "Enter your message here"
      } else {
        chatTextArea.placeholder = "You are muted till the end of the game"
        chatTextArea.value = "";
      }

      // check permission to play
      var gameSubmitArea = document.getElementById("submit-menu");
      gameSubmitArea.style.display = data["permissions"]["can_play"] ? 'block' : 'none';

      // check change-stream permissions
      var streamChangeArea = document.getElementById("set-stream-menu");
      streamChangeArea.style.display = data["permissions"]["can_change_stream"] ? 'block' : 'none';

      // check check-submissions permissions
      var chatArea = document.getElementById("chat");
      var emotesArea = document.getElementById("emotes-panel");
      var submissionsMenu = document.getElementById("submissions-menu");
      if (data["permissions"]["can_check_submissions"]){
        chatArea.style.aspectRatio = "2/1";
//        emotesArea.style.display = 'none';
        submissionsMenu.style.display = 'block';
      } else {
        chatArea.style.aspectRatio = "400/705";
        submissionsMenu.style.display = 'none';
//        emotesArea.style.display = 'block';
      }

      // check permission to moderate chat
      showChatModeration = data["permissions"]["can_moderate_chat"];

      // check permission to moderate users
      showUserModeration = data["permissions"]["can_manage_users"];

      // show submit menu
      showSubmitMenu = data["permissions"]["can_play"];

      // check whether can rule the game
      canChangeLeaderboard = data["permissions"]["can_change_leaderboard"];

  });
  socket.on('score', function(data) {
      $('#leaderboard').empty();
      for (const user of data["players"]) {
         var color = (user["is_online"]) ? "white" : "grey";
         var badges = "";
         if (user["can_manage_users"]) badges += '<img alt src="https://static-cdn.jtvnw.net/badges/v1/5527c58c-fb7d-422d-b71b-f309dcb85cc1/1">';
         if (user["can_moderate_chat"]) badges += '<img alt src="https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1">';
         if (!user["can_chat"]) badges += '<img alt src="static/images/chat-mute-custom.PNG" height=20px>';
         $('#leaderboard').append('<div class="person_div"><div class="person_name"><span class="username" style="color: ' + color + ';">' + user["username"] + '</span>' + badges + '</div><div class="person_score">' + user["points"] + '</div></div>');
      }
      $('#viewers').empty();
      for (const user of data["viewers"]) {
         var color = (user["is_online"]) ? "white" : "grey";
         var badges = "";
         if (user["can_manage_users"]) badges += '<img alt src="https://static-cdn.jtvnw.net/badges/v1/5527c58c-fb7d-422d-b71b-f309dcb85cc1/1">';
         if (user["can_moderate_chat"]) badges += '<img alt src="https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1">';
         if (!user["can_chat"]) badges += '<img alt src="static/images/chat-mute-custom.PNG" height=20px>';
         $('#viewers').append('<div class="person_div"><div class="person_name"><span class="username" style="color: ' + color + ';">' + user["username"] + '</span>' + badges + '</div></div>');
      }
      document.getElementById("viewers").style.display = data["viewers"].length == 0 ? 'none' : 'block';
      document.getElementById("viewers-title").style.display = data["viewers"].length == 0 ? 'none' : 'block';
      document.getElementById("leaderboard").style.display = data["players"].length == 0 ? 'none' : 'block';
      document.getElementById("leaderboard-title").style.display = data["players"].length == 0 ? 'none' : 'block';
  });
  socket.on('result', function(data) {
      result_type = data["type"];
      result_val = data["result"];
      if (result_type == "submitter") $('#submitter-score').html(result_val);
      if (result_type == "author") $('#author-score').html(result_val);
  });
  socket.on('prediction-queue', function(data) {
      // data = [{username: str, submissions: [{song: str, submitter: str}]}]
      $('#guesses').empty();
      for (const submissions of data){
          var username = submissions["username"];
          var submissionHtml = '<div class="submission-username">' + username + '</div>';
          for (const [submissionIdx, submission] of submissions["submissions"].entries()){
              submissionHtml += '<div class="submission-guess"><input type="number" step="any" name="score" min="0" id="submission-' + username + '-' + submissionIdx + '" value="' + (submission["processed"] ? submission["score"] : '') + '"><button onclick=set_score(\"' + username + '\",' + submissionIdx + ')>x</button><div class="submission-texts"><div class="row guess-song-title" style="color: ' + (submission["processed"] ? "black" : "red") + ';">' + submission["song"] + '</div><div class="row guess-author" style="color: ' + (submission["processed"] ? "black" : "red") + ';">' + submission["submitter"] + '</div></div></div>';
          }
          if (canChangeLeaderboard)
            submissionHtml += '<div class="submission-final-score">Final score: <input type="number" name="score" min="0" value="" align="center" id="final-score-' + username + '"></div>';
          $('#guesses').append('<div class="user-submission bg-white-transparent mb-3" data-username="' + username + '">' + submissionHtml + '</div>');
      }
      if (canChangeLeaderboard)
        $('#guesses').append('<button id="queue-management-button" onclick="give_final_score();">' + 'Give final score and end the round' + '</button>');
  });
  socket.on('stream-change', function(data) {
      link = data["link"];
      if (document.getElementById('stream').src != link)
        document.getElementById('stream').src = link;
  });
  socket.on('clear-chat', function(data) {
      for (const msgId of data){
        var element = document.getElementById('msg_' + msgId);
        if (element) {
          element.innerHTML = "[message deleted]";
        }
      }
  });
  socket.on('redirect', function(data) {
      socket.disconnect();
      // go back to the login page
      window.location.href = location.protocol + '//' + document.domain + ':' + location.port + '/';
  });
  $('#change-leaderboard').click(function(e) {
      text = $('#admin-leaderboard').val();
      if (!text) return;
      socket.emit('leaderboard-change', {data: text});
  });
  $('#change-stream').click(function(e) {
      text = $('#stream-link').val();
      if (!text) return;
      socket.emit('stream-change', {link: text});
  });
  $('#default-stream').click(function(e) {
      socket.emit('stream-change', {link: "default"});
  });
  $('#send').click(function(e) {
      text = $('#text').val();
      if (!text) return;
      $('#text').val('');
      socket.emit('text', {msg: text});
  });
  $('#prediction-submit').click(function(e) {
      submitter = $('#submitter-input').val();
      author = $('#author-input').val();
      if (!submitter && !author) {
          alert("At least submitter or an author must be guessed :3");
          return;
      };
      $('#submitter-input').val('');
      $('#author-input').val('');
      if (!submitter) submitter = '';
      if (!author) author = '';
      socket.emit('prediction', {author: author, submitter: submitter});
  });
  $('#okak').click(function(e) {
      socket.emit('text', {msg: 'okak'});
  });
  $('#wowie').click(function(e) {
      socket.emit('text', {msg: 'wowie'});
  });
  $(this).find('input').keypress(function(e) {
      // Enter pressed?
      if(e.which == 10 || e.which == 13) {
          text = $('#text').val();
          if (!text) return;
          $('#text').val('');
          socket.emit('text', {msg: text});
      }
  });
});

function leave_room() {
  socket.emit('left', {}, function() {
      socket.disconnect();
      // go back to the login page
      window.location.href = location.protocol + '//' + document.domain + ':' + location.port + '/';
  });
};

function delete_message(blockId, allMessages, muteUser) {
  socket.emit('chat-action', {msg_id: blockId, all: allMessages, mute: muteUser});
};

function set_permission(username, permission, value) {
  socket.emit('set-permission', {username: username, permission: permission, value: value});
};

function give_final_score() {
  var allSubmissions = document.getElementById('guesses');
  var finalScores = {};
  for (const userSubmissions of allSubmissions.childNodes){
      if (!userSubmissions.hasAttribute("data-username")) continue;

      var username = userSubmissions.getAttribute("data-username");
      var stringScore = document.getElementById('final-score-' + username).value;

      if (isNaN(parseInt(stringScore))) {
          alert("No final score for user: " + username);
          return;
      }
      finalScores[username] = parseInt(stringScore);
  }
  socket.emit('update-leaderboard', finalScores);
};


function make_user_management_menu(username, data) {
  $('#user-context-menu').empty();
  for (const permission of data){
    $('#user-context-menu').append('<button onclick=set_permission(\"' + username + '\",\"' + permission["name"] + '\",' + !permission["value"] + ')>' + permission["name"] + ' : ' + permission["value"] + '</button>');
  }
};

function set_score(username, submissionIdx) {
  var score = document.getElementById("submission-" + username + '-' + submissionIdx).valueAsNumber;
  socket.emit('set-score', {username: username, submission: submissionIdx, score: score});
};

function add_emote(text){
  var chatTextArea = document.getElementById("text");
  if (chatTextArea.disabled) return;
  $('#text').val($('#text').val() + text);
  document.getElementById("text").focus();
};
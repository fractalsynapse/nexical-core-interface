window.onbeforeunload = function () {
  window.scrollTo(0, 0);
};

$(function () {
  $('textarea').on('keyup keypress', function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });
  $('textarea').each(function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });

  $('#message-subject').on('keyup keypress', function () {
    var text = $(this).val();
    if (text.indexOf('<<') != -1 || text.indexOf('>>') != -1) {
      $(this).addClass('invalid-token');
      $('#send-button').prop('disabled', true);
    } else {
      $(this).removeClass('invalid-token');
      $('#send-button').prop('disabled', false);
    }
  });
  $('#message-subject').each(function () {
    var text = $(this).val();
    if (text.indexOf('<<') != -1 || text.indexOf('>>') != -1) {
      $(this).addClass('invalid-token');
      $('#send-button').prop('disabled', true);
    }
  });

  $('#message-body').on('keyup keypress', function () {
    var text = $(this).val();
    if (text.indexOf('<<') != -1 || text.indexOf('>>') != -1) {
      $(this).addClass('invalid-token');
      $('#send-button').prop('disabled', true);
    } else {
      $(this).removeClass('invalid-token');
      $('#send-button').prop('disabled', false);
    }
  });
  $('#message-body').each(function () {
    var text = $(this).val();
    if (text.indexOf('<<') != -1 || text.indexOf('>>') != -1) {
      $(this).addClass('invalid-token');
      $('#send-button').prop('disabled', true);
    }
  });

  $('#send-button').on('click', function (event) {
    event.preventDefault();

    $.ajax({
      method: 'POST',
      url: $(this).attr('data-url'),
      headers: {
        'X-CSRFTOKEN': $('#csrf-token').val(),
      },
      data: {
        subject: $('#message-subject').val(),
        body: $('#message-body').val(),
      },
    }).done(function (data) {
      location.reload();
    });
  });

  $('#skip-button').on('click', function (event) {
    event.preventDefault();

    $.ajax({
      method: 'POST',
      url: $(this).attr('data-url'),
      headers: {
        'X-CSRFTOKEN': $('#csrf-token').val(),
      },
      data: {},
    }).done(function (data) {
      location.reload();
    });
  });

  $('#block-button').on('click', function (event) {
    event.preventDefault();

    $.ajax({
      method: 'POST',
      url: $(this).attr('data-url'),
      headers: {
        'X-CSRFTOKEN': $('#csrf-token').val(),
      },
      data: {},
    }).done(function (data) {
      location.reload();
    });
  });
});

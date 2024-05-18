$(function () {
  $('.token-button').on('click', function () {
    $.get($(this).attr('data-url')).done(function (data) {
      location.reload();
    });
    return false;
  });

  $('#token-copy').on('click', function () {
    navigator.clipboard.writeText($('#token-value').text().trim());
    return false;
  });
});

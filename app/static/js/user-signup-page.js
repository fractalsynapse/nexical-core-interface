$(function () {
  var explanation_state = 0;

  $('#explanation-toggle-button').on('click', function (event) {
    event.preventDefault();

    if (explanation_state == 1) {
      $('#explanation-toggle-button').text('Open references');
      $('#explanation-statements').addClass('d-none');
      explanation_state = 0;
    } else {
      $('#explanation-toggle-button').text('Close references');
      $('#explanation-statements').removeClass('d-none');
      explanation_state = 1;
    }
  });
});

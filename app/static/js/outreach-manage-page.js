window.onbeforeunload = function () {
  window.scrollTo(0, 0);
};

function reinitialize_textareas() {
  $('textarea').on('keyup keypress', function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });
  $('textarea').each(function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });

  $('#column-view-toggle').on('click', function (event) {
    $('#campaign-columns').toggle();
    $(this).text($(this).text() == 'Expand' ? 'Collapse' : 'Expand');
  });

  $('.token-view-toggle').on('click', function (event) {
    $(this).parents('.token-wrapper').find('.token-table').toggle();
    $(this).text(
      $(this).text() == 'Expand Tokens' ? 'Collapse Tokens' : 'Expand Tokens',
    );
  });
}

function update_email_add_button() {
  if ($('.email-form:not(.d-none)').length == 10) {
    $('.email-add-wrapper').hide();
  } else {
    $('.email-add-wrapper').show();
  }
}

function reinitialize_table(id) {
  $(`#${id} .delete-button`).on('click', function () {
    var $tr = $(this).closest('tr');
    var basename = $tr.attr('data-basename');

    $tr.addClass('d-none');

    var $input = $('<input />', {
      type: 'checkbox',
      name: `${basename}-DELETE`,
      id: `id_${basename}-DELETE`,
      checked: true,
    });
    $tr.find('td.delete').append($input);
    update_email_add_button();
    reinitialize_textareas();
  });
  update_email_add_button();
  reinitialize_textareas();
}

$(function () {
  reinitialize_table('email-form-table');

  $('#add-email').on('click', function () {
    var $new_form = $('#email-empty-form').clone();
    var form_index = parseInt($('#id_emails-TOTAL_FORMS').val());

    $new_form.removeClass('d-none').addClass('email-form');
    $new_form.attr('data-basename', `email-${form_index}`);

    $form_div = $new_form.find('div');
    $form_div.attr(
      'id',
      $form_div.attr('id').replace('__prefix__', form_index),
    );

    $form_label = $new_form.find('label');
    $form_label.attr(
      'for',
      $form_label.attr('for').replace('__prefix__', form_index),
    );

    $form_input = $new_form.find('input');
    $form_input.attr(
      'id',
      $form_input.attr('id').replace('__prefix__', form_index),
    );
    $form_input.attr(
      'name',
      $form_input.attr('name').replace('__prefix__', form_index),
    );

    $('#email-form-table').append($new_form);
    $('#id_emails-TOTAL_FORMS').attr('value', form_index + 1);

    reinitialize_table('email-form-table');
  });
});

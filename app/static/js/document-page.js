function sleep(ms = 0) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function update_file_add_button() {
  if ($('.file-form:not(.d-none)').length == 10) {
    $('.file-add-wrapper').hide();
  } else {
    $('.file-add-wrapper').show();
  }
}

function update_bookmark_add_button() {
  if ($('.bookmark-form:not(.d-none)').length == 10) {
    $('.bookmark-add-wrapper').hide();
  } else {
    $('.bookmark-add-wrapper').show();
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
    update_file_add_button();
    update_bookmark_add_button();
  });
  update_file_add_button();
  update_bookmark_add_button();
}

$(function () {
  reinitialize_table('file-form-table');
  reinitialize_table('bookmark-form-table');

  $('textarea').on('keyup keypress', function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });
  $('textarea').each(function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });

  $('.document-progress').each(async function () {
    var $element = $(this);
    var progress_url = $element.attr('data-url');
    var continue_processing = true;

    while (continue_processing) {
      $.get(progress_url).done(function (data) {
        if ('processed_time' in data && data['processed_time']) {
          $element.find('.document-processing').addClass('d-none');
          $element.find('.document-time-icon').removeClass('d-none');
          continue_processing = false;
        }
      });
      await sleep(2000);
    }
  });

  $('#add-files').on('click', function () {
    var $new_form = $('#file-empty-form').clone();
    var form_index = parseInt($('#id_files-TOTAL_FORMS').val());

    $new_form.removeClass('d-none').addClass('file-form');
    $new_form.attr('data-basename', `files-${form_index}`);

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

    $form_textarea = $new_form.find('textarea');
    $form_textarea.attr(
      'id',
      $form_textarea.attr('id').replace('__prefix__', form_index),
    );
    $form_textarea.attr(
      'name',
      $form_textarea.attr('name').replace('__prefix__', form_index),
    );

    $('#file-form-table').append($new_form);
    $('#id_files-TOTAL_FORMS').attr('value', form_index + 1);

    reinitialize_table('file-form-table');
  });

  $('#add-bookmarks').on('click', function () {
    var $new_form = $('#bookmark-empty-form').clone();
    var form_index = parseInt($('#id_bookmarks-TOTAL_FORMS').val());

    $new_form.removeClass('d-none').addClass('bookmark-form');
    $new_form.attr('data-basename', `bookmarks-${form_index}`);

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

    $form_textarea = $new_form.find('textarea');
    $form_textarea.attr(
      'id',
      $form_textarea.attr('id').replace('__prefix__', form_index),
    );
    $form_textarea.attr(
      'name',
      $form_textarea.attr('name').replace('__prefix__', form_index),
    );

    $('#bookmark-form-table').append($new_form);
    $('#id_bookmarks-TOTAL_FORMS').attr('value', form_index + 1);

    reinitialize_table('bookmark-form-table');
  });
});

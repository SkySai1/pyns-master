function get_all(what, remove, edit, sw){
  $.ajax({
    url: what,
    method: 'POST',
    dataType: 'json'
  })    
  .done(function(data) {
    if (data){
      for (row of data){
        create_row(what, row[0], row[1], row[2], remove, edit, sw)
      }
  }
  })
  .fail(function(data, s, e){

  });  
}


function create_row(what, object, id, state, remove, edit, sw){
  if (state == true || state == "True") {
    var checked = 'checked'
  } else {
    var checked = ''
    var check = document.getElementById('o-sw-all');
    check.checked = false;
  }

  var table = $('#o_list')
  var row = $(`<tr id="row_${object}" class="row-o"></tr>`)
  var pos = $('.row-o').length + 1
  var number = $(`<td>${pos}</td>`)
  var active = $(`<td><input class="o-sw" type="checkbox" ${checked} onchange="switch_object('${what}','${object}', '${sw}', this.checked)"/></td>`)
  var name = $(`<td><input id="o_${id}" class="o-name" value="${object}" disabled></td>`)
  var edit = $(`<td><button id="o-ch_${pos}" onclick="edit_object('${what}','o_${id}', this, '${edit}')">Ручка</button></td>`)
  var trash = $(`<td><button onclick="mv_object('${what}','${id}', '${remove}')">Корзина</button></td>`)
  var select = $(`<td><input id="sel-o_${id}" class="sel-o-all" type="checkbox"></td>`)

  row.append(number)
  row.append(active)
  row.append(name)
  row.append(edit)
  row.append(trash)
  row.append(select)

  table.append(row)
}


function new_object(what, data, action, isimport){
      $("#message").text('');
      var object = data[0]['value']
      var request = new Promise(function(resolve, reject) {$.ajax({
        url: what + '/' + object + '/' + action,
        method: 'POST',
        dataType: 'json',
        data: data,
      })    
      .done(function(data) {
        if (!isimport){
          //location.reload();
        }
        create_row(what, data['object'], data['id'], true, data['remove'], data['edit'], data['switch'])
        resolve(data)
          //$('#d_list').prepend(`<tr><td>-</td><td>${data}</td></tr>`)
      })
      .fail(function(data, s, e){
        var message = $("#message")
        switch (data.responseText) {
          case 'exist': message.append(`${object} уже существует\n`); break;
          case 'badname': message.append(`${object} - неккоректное DNS имя\n`); break;
          default: break;}
      })}
      )
    return request
};

async function mv_object(what, obj, action){
  $.ajax({
    url: what + '/' + obj + '/' + action,
    method: 'POST',
    dataType: 'json',
    data: [obj],
  })    
  .done(function(data) {
    id = `#o_${data[0]}`
    var row = $(id).closest('tr')
    row.remove()
  })
  .fail(function(data, s, e){

  });
};

function switch_object(what, obj, action, state){
  
  $.ajax({
    url: what + '/' + obj + '/' + action,
    method: 'POST',
    dataType: 'json',
    data: {"state": state},
  })    
  .done(function(data) {
    if (obj == '*') {
      $('.o-sw').each(function(i, obj){
        var row = $(obj).parent().parent()
        if (row.css('display') != 'none') {        
          obj.checked = state;
        }
      })
    } else {
      var check = true
      $('.o-sw').each(function(i, obj){
        if (obj.checked == false){
          check = false}
      })
      document.getElementById('o-sw-all').checked = check;     
    }
  })
  .fail(function(data, s, e){

  });
};

function edit_object(what, field_id, button, action){
  console.log(field_id)
  field = $(`#${field_id}`)
  var obj =  field.attr("value")
  if (field.attr('disabled')) {
    field.prop('disabled', false);
    $(button).text('Дискета')
  } else {
    var newval = field.val()
    if (newval != field.attr("value")){
      $.ajax({
        url: what + '/' + obj + '/' + action,
        method: 'POST',
        dataType: 'json',
        data: {"new": newval},
        success: function(data) {
          field.attr("value", data[0])
          field.prop('disabled', true);
          $(button).text('Ручка')
        },
        error: function(data, s, e) {
          if (data.responseText == 'badname') {
            alert('Bad Name')
          };
        }
      })
    } else {
      field.prop('disabled', true);
      $(button).text('Ручка')
    };
  };
}

function search_object(field) {
  var origin = $(field).val().toLowerCase()
  var pattern = new RegExp(origin, 'g')
  $('.o-name').each(function (i, obj) {
    var row = $(this).closest('tr')
    if (!obj.value.match(pattern)) {
      $(row).css("display", "none");
    } else {
      $(row).css("display", "");
    }
  });
}

function object_import(what, input, action){
  let file = input.files[0];
  input.value = '';
  let reader = new FileReader();

  reader.onload = function(e) {
    var result = JSON.parse(e.target.result);
    if (Object.keys(result).length > 0){
      localStorage.setItem('import_fails', '')
      $("#hmsg").text('')
      for (object of result){
        var promises = []
        var data = [{'value': object}]
        promises.push(new_object(what, data, action, true));
        }
      Promise.all(promises)
        .then(result => {})
        .catch(error => {})
      }
    }

  reader.readAsText(file)
}

function remove_selected_objects(what, action){
  var array = $('.sel-o-all').map(function(){
    if (this.checked){
    return this};
  }).get()
  array.forEach(async (item) => {
    var id = item.id.replace("sel-o_",'')
    await mv_object(what, id, action)
  });
  document.getElementById('check_o_all').checked = false;
}

function select_objects(state){
  $('.sel-o-all').each(function(i, obj){
    var row = $(obj).parent().parent()
    if (row.css('display') != 'none') {
      obj.checked = state
    }
  })
}
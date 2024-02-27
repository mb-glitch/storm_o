$(".js-data-example-ajax").select2({
  ajax: {
    url: "http://192.168.0.133:8000/wyniki/pacjenci/",
    dataType: 'json',
    delay: 250,
    data: function (params) {
      return {
        q: params.term, // search term
        page: params.page
      };
    },
    processResults: function (data, params) {
      // parse the results into the format expected by Select2
      // since we are using custom formatting functions we do not need to
      // alter the remote JSON data, except to indicate that infinite
      // scrolling can be used
      params.page = params.page || 1;
      return {
        results: data.results,
        pagination: {
          more: (params.page * 30) < data.total_count
        }
      };
    },
  },
  width: '100%',
  placeholder: 'Szukaj pacjenta',
  minimumInputLength: 4,
  language: "pl"
});



setTimeout(function(){
   window.location.reload(true);
}, 610000);

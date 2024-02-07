$(document).ready(function(){
  const ddmenu = $(".dropdown-menu")
  $(".dropdown-toggle").on('click', function(){ ddmenu.toggle() });

  $(document).on('click', function(event) {
      if (!$(event.target).closest('.dropdown').length) { ddmenu.hide() }
  });
});


// $(document).ready(function(){
//   const ddmenu = $("#dropdown-menu-new")
//   $("#dropdownMenuButton").on('click', function(){ ddmenu.toggle() });

//   $(document).on('click', function(event) {
//       if (!$(event.target).closest('.dropdown').length) { ddmenu.hide() }
//   });
// });
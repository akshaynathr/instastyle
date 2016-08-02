var Global=0;
$(document).ready(function()
		{	
var pagination_count=0;
getFeed(pagination_count);



$(window).scroll(function() {

	if($(window).scrollTop()+$(window).height()>$(document).height()-500 && Global==1)	{
	//alert("near bottom");
	
$('.container').append('<img id="loading" style="margin-left:100px;"src="static/images/loader.gif">');
	getFeed(++pagination_count);
}
});


//$('.insert').empty();

$('.container').append('<img id="loading" style="margin-left:100px;" src="static/images/loader.gif">');


});


function getFeed(no)
{
	var url='/myfeed/';
	var apiKey=$('#dummy').text().trim();
//alert(apiKey);
	url=url+apiKey+'/'+no

	$.ajax({
        url:url,
        success:function(data){ /*alert(JSON.stringify(data));*/createAndInsert(data);},
        error:function(data) {/*alert("error:"+JSON.stringify(data));*/ alert("Error loading content. Please refresh the page.");}

		});


}


function createAndInsert(data)
{

	if(data['feed'].length==0 && Global==0)
	{
		// alert('nodata');

	$('#loading').remove();
	}
	
else	if(data['feed'].length==0 && Global ==1) {//intro_insert(0);}
	$('#loading').remove();		}

		else {

Global=1;
// alert(data['feed'].length);
for(var i=0;i<data['feed'].length;i++)
  {
	var img_url=data['feed'][i]['image'];
	var user_image=data['feed'][i]['user_image'];
	 
	var title=data['feed'][i]['title'];
	// var views=data['feed'][i]['views'];
	// var url=data['feed'][i]['url'];
	// var domain=data['feed'][i]['domain'];
	var id=data['feed'][i]['id'];
	var name=data['feed'][i]['name'];
	var desc=data['feed'][i]['desc'];
	var date=data['feed'][i]['date'];
	date=new Date(date);
		
	// var Text=text.slice(0,200)+'...';
	// if (img_url.trim()=='') img_url='static/images/img_broken.jpg';
	create(img_url,user_image,title,name,id,desc,date);

	}
		}
}


// $('#myModal').on('hidden.bs.modal', function () {

 
// 	$('.modal-title').html(''); 
// 	$('#modal_img').attr('src','');
// 	// $('.data').html(data['feed'][0]['text']);

// 	$('.modal-body').empty();
//     // do something…
// });


function create(img_url,user_image,title,name,id,desc,date)
{//alert(img_url);$('.modal-body').empty();
	$('#loading').remove();
	 
	 $('.container').append(

	 	 
		'<div class="row" >'+
			'<div class="col-md-3" > </div>'+
			'<div class="col-md-6" style="background-color:rgb(248,248,248);border-radius:10px;margin-top:10px;"> ' +
							'<hr/>'+
				'<div style="margin-bottom:10px;"><img src=static/uploads/'+user_image+' style="width:30px; height:30px; border-radius:100%"><b> '+name+'</b><p style="float:right; font-size:10px; padding-top:10px;"> '+date.toDateString()+ '</p> </div>'+
				'<h5 style="color:rgba(0,0,0,.6);padding-top:2%;padding-left:1%;">'+title+'</h5>'+
				'<div class="stretch" style="  background: url(static/uploads/'+img_url+') no-repeat ;-webkit-background-size: contain;-moz-background-size: contain;-o-background-size: contain;background-size: contain;width:100%;height:300px; "> </div>'+

				'<img  src="static/love.jpg" style="display:inline;width:35px; height:40px; border-radius:100%; ">  <p style="display:inline"> 144</p>'+ 
				'<div style="float:right; padding:1%;">'+

				'	<img src="" style="width:25px; height:25px; border-radius:100%">  '+
				'</div>'+


      '<div style="display:block;text-align:center;">'  	+ desc+
      '</div>'+
      '<hr>'+
			'</div>'+
			'<div class="col-md-3" style="text-align:center; padding-top:10%;" >'+

			 

				 

			'</div>'+


	   ' </div>'
	   );
		 

 


}



 

jQuery.noConflict();

function gtid(x){
	if(x!=undefined) return "<strong> "+x+" </strong><br/>";
	return "<br/>";
}

function gtname(x){
	if(x!=undefined) return "<a name=\""+x+"\"></a>";
	return " ";
}

function clearsubdashes(x){
	         var a = new RegExp(String.fromCharCode(95),'g');
                              x = x.replace(a, String.fromCharCode(32));
	          return x;
}

jQuery(document).ready( 
	function(){ 
	jQuery('.proposition').css('color','#006500');
	jQuery('.lemma').css('color','#006500');
	jQuery('.corollary').css('color','#006500');

	var typ = new Array(".section",".subsection",".subsubsection",".paragraph",".subparagraph");
	for(k=0;k<typ.length;k++){
		jQuery(typ[k]).each( function(){var kk = k+2;jQuery(this)
		.before('<h'+kk+'>'+ jQuery(this).attr('id')+'</h'+kk+'>'+gtname(jQuery(this).attr('name')))
		.wrap('<blockquote></blockquote>')});	
	}

	  jQuery('.enumerate').each( function(){jQuery(this)
	.wrap('<ol></ol>')});
	

	  jQuery('.description').each( function(){jQuery(this)
	.wrap('<dl></dl>')});
	
	  jQuery('.itemize').each( function(){jQuery(this)
	.wrap('<ul></ul>')});
	
	  jQuery('.item').each( function(){jQuery(this)
	.wrap('<li></li>')});
	


	var hd = new Array("h1","h2","h3","h4","h5","h6");
	for(k=0;k<hd.length;k++){
		jQuery(hd[k]).each( function(){var y = jQuery(this).html();
		jQuery(this).html(clearsubdashes(y));
		})	
	}

	var typp = new Array(".theorem",".proposition",".lemma",".corollary",".remark",".example");
	for(k=0;k<typp.length;k++){
	var current = typp[k].substring(1,2).toUpperCase()+typp[k].substring(2);
               jQuery(typp[k]).each( function(){jQuery(this)
	.before('&#xa0;<br/><strong> '+current
	+' </strong>&#xa0; '+gtid(jQuery(this).attr('id'))+gtname(jQuery(this).attr('name')) )
	.wrap('<blockquote></blockquote>')});
	}
          
	jQuery('.proof').before('&#xa0;<br/><i>Proof</i>&#xa0;');

	jQuery('.equation').each( function(){jQuery(this)
	.before('&#xa0;<br/>'+gtname(jQuery(this).attr('num')))
	.append('<num class="eqno">('+jQuery(this).attr('num')+')</num>')});

	jQuery('.eq').before('&#xa0;<br/>');

	jQuery('.skip').replaceWith('<p/>&#xa0;<p/>');
	jQuery('.quad').replaceWith('&#xa0;&#xa0;&#xa0;');
	jQuery('.qquad').replaceWith('&#xa0;&#xa0;&#xa0;&#xa0;&#xa0;');
	jQuery('.cr').replaceWith('<br/>');

	jQuery('.ref').each( function(){jQuery(this)
	.replaceWith("<a href=\"#"+jQuery(this).attr('name')+"\">"+jQuery(this).text()+"</a>")});
	jQuery('.labelref').each( function(){jQuery(this)
	.replaceWith("<a href=\"#"+jQuery(this).attr('name')+"\">"+jQuery(this).attr('name')+"</a>")});

	jQuery('proposition').css('color','#006500');
	jQuery('lemma').css('color','#006500');
	jQuery('corollary').css('color','#006500');

	var typ = new Array("section","subsection","subsubsection","paragraph","subparagraph");
	for(k=0;k<typ.length;k++){
		jQuery(typ[k]).each( function(){var kk = k+2;jQuery(this)
		.before('<h'+kk+'>'+ jQuery(this).attr('id')+'</h'+kk+'>'+gtname(jQuery(this).attr('name')))
		.wrap('<blockquote></blockquote>')});	
	}

	var hd = new Array("h1","h2","h3","h4","h5","h6");
	for(k=0;k<hd.length;k++){
		jQuery(hd[k]).each( function(){var y = jQuery(this).html();
		jQuery(this).html(clearsubdashes(y));
		})	
	}

	  jQuery('enumerate').each( function(){jQuery(this)
	.wrap('<ol></ol>')});
	

	  jQuery('description').each( function(){jQuery(this)
	.wrap('<dl></dl>')});
	
	  jQuery('itemize').each( function(){jQuery(this)
	.wrap('<ul></ul>')});
	
	  jQuery('item').each( function(){jQuery(this)
	.wrap('<li></li>')});
	

	var typp = new Array("theorem","proposition","lemma","corollary","remark","example");
	for(k=0;k<typp.length;k++){
	var current = typp[k].substring(0,1).toUpperCase()+typp[k].substring(1);
               jQuery(typp[k]).each( function(){jQuery(this)
	.before('&#xa0;<br/><strong> '+current
	+' </strong>&#xa0; '+gtid(jQuery(this).attr('id'))+gtname(jQuery(this).attr('name')) )
	.wrap('<blockquote></blockquote>')});
	}
          
	jQuery('proof').before('&#xa0;<br/><i>Proof</i>&#xa0;');

	jQuery('equation').each( function(){jQuery(this)
	.before('&#xa0;<br/>'+gtname(jQuery(this).attr('num')))
	.append('<num class="eqno">('+jQuery(this).attr('num')+')</num>')});

	jQuery('eq').before('&#xa0;<br/>');

	jQuery('skip').replaceWith('<p/>&#xa0;<p/>');
	jQuery('quad').replaceWith('&#xa0;&#xa0;&#xa0;');
	jQuery('qquad').replaceWith('&#xa0;&#xa0;&#xa0;&#xa0;&#xa0;');
	jQuery('cr').replaceWith('<br/>');

	jQuery('ref').each( function(){jQuery(this)
	.replaceWith("<a href=\"#"+jQuery(this).attr('name')+"\">"+jQuery(this).text()+"</a>")});
	jQuery('labelref').each( function(){jQuery(this)
	.replaceWith("<a href=\"#"+jQuery(this).attr('name')+"\">"+jQuery(this).attr('name')+"</a>")});

	var y = jQuery("a.reflink:last").text();
	if(y.indexOf("Contents")>0){
	jQuery("a.reflink:last").prepend("&#xa0;&#xa0;").append("&#x21ba;");
	} else {		
		jQuery("a.reflink:last").prepend("&#xa0;&#xa0;").append("&#x21aa;");	
	}	
	jQuery("a.reflink").not(':last').prepend("&#xbb;");	

	jQuery("li.page_item").not(".current_page_parent").prepend("&#xa0;&#xa0;").css('font-size','90%');	
	jQuery("li.current_page_parent").prepend("&#xa0;&#x21b0;&#xa0;").css('font-size','111%');	
	jQuery('#tabs').wrap('<p/><br/><p/>');
       });	


 


function on_click(btn) {
	if (btn.attributes['xaal-addr']) {
		addr = btn.attributes['xaal-addr'].value;
		console.log('click:' + addr);
		url = '/api/click/'+addr+'/0';
		fetch(url);
    }
}

function on_dclick(btn) {
	if (btn.attributes['xaal-addr']) {
		addr = btn.attributes['xaal-addr'].value;
		console.log('dclick:' + addr);
		url = '/api/click/'+addr+'/1';
		fetch(url);
    }
}

function on_toggle(btn) {
	addr = btn.attributes['xaal-addr'].value;
	if (btn.checked == true) {
		url = '/api/set_on/'+addr
	}
	else {
		url = '/api/set_off/'+addr
	}
	console.log(url);
	fetch(url);
}

// common.js

function check_url(url) {
	let filter_url = "";

	for (let i = 0; i < $allow_url.length; i++) {
		const pattern = $allow_url[i];
		if (pattern.test(url) !== false) {
			filter_url = url;
		}
	}

	for (let i = 0; i < $deny_url.length; i++) {
		const pattern = $deny_url[i];
		if (pattern.test(url) !== false) {
			filter_url = "";
		}
	}

	return filter_url !== "";
}

function get_requested_url(relative_url) {
	relative_url = relative_url.toString();
	if (relative_url === "#") {
		return relative_url;
	} else {
		let url_prefix_list = [$base_url, $server_url, $path];
		for (let url_prefix of url_prefix_list){
			if (relative_url.startsWith(url_prefix)) {
				try{
					let new_m_url = relative_url.substring(url_prefix.length);
					let url_obj = new URL($url);
					let new_m_url_obj = new URL(new_m_url, url_obj.origin);
					if (check_url(new_m_url_obj.href)) {
						return $path + new_m_url_obj.href;
					}
				} catch (e) {
					continue;
				}
			}
		}
		let abs_url = new URL(relative_url, $url).href;
		if (check_url(abs_url)) {
			return $path + abs_url;
		} else {
			return relative_url;
		}
	}
}

function redirect_log(name, original_url, new_url) {
    if (original_url !== new_url) {
    	console.debug(name + ": Redirect " + original_url + " to " + new_url);
    }
}

def DownloadChromeExtension(id_or_url:str, output_file:str, chromeversion:str='125.0.6422.113'):
    from urllib.parse import urlparse
    from urllib.parse import urlencode
    from urllib.request import urlopen
    import os

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    try:
        ext_url = urlparse(id_or_url)
        ext_id = os.path.basename(ext_url.path)
    except:
        ext_id = id_or_url

    crx_base_url = 'https://clients2.google.com/service/update2/crx'
    crx_params = urlencode({
        'response': 'redirect',
        'prodversion': chromeversion, # chrome的版本
        'acceptformat': 'crx2,crx3',
        'x': 'id=' + ext_id + '&uc'
    })

    crx_url = crx_base_url + '?' + crx_params
    crx_path = output_file if output_file is not None else ext_id + '.crx'

    with open(crx_path, 'wb') as file:
        file.write(urlopen(crx_url).read())

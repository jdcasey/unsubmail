import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs
import json
import re

def ngpvan_unsub(url, baseurl, html, form_obj, form_params):
    match = re.search(r"\$scope.contact\s*=\s*(\{[^;]+);", html)
    if match is not None:
        contact = json.loads(match.group(1))

        form_params.update({
            'id': contact.get('VanId'),
            'emailMessageContentId': contact.get('EmailMessageContentId'),
            'emailAddress': contact.get('EmailAddress'),
            'unsubscribe': True,
            'distributionId': contact.get('DistributionId'),
            'distributionUniqueId': contact.get('DistributionUniqueId')
        })

        try:
            resp = requests.post(f"{baseurl}/Unsubscribe/Update", params=form_params)
            print(f"ngpvan Unsubscribe response: {resp.status_code}")
            return resp.status_code == 200
        except Exception as e:
            print(f"Failed to send HTTP request for unsubscribe: {str(e)}")

        return False

def myngp_unsub(url, baseurl, html, form_obj, form_params):
    form_params['DoNotEmail']=True
    try:
        resp = requests.post(url, params=form_params)
        print(f"myngp Unsubscribe response: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Failed to send HTTP request for unsubscribe: {str(e)}")

    return False


fnmap = {
    'email.ngpvan.com': ngpvan_unsub,
    'act.myngp.com': myngp_unsub
}

def process_unsub(url):
    print(f"Processing:\n\n    {url}\n\n")

    try:
        resp = requests.get(url)
    except Exception as e:
        print(f"Failed to send initial HTTP request for unsubscribe: {str(e)}")
        return False

    # print(resp)

    if resp.status_code != 200:
        print(f"The unsubscribe request appears to have failed! {resp.status_code}")

    soup = bs(resp.text, 'html.parser')

    up = urlparse(url)
    urlpath = up.path
    # print(f"\nOriginal URL path: '{urlpath}'")
    idx = url.index(urlpath)

    baseurl = url[0:idx]
    print(f"Got base URL: {baseurl}")

    if soup.body is None:
        return True

    forms = soup.body.find_all('form')
    form = None
    for f in forms:
        if 'search' not in str(f):
            form = f
            break

    if form is not None:
        # print(f"Processing form: {form}")

        valmap = {}
        for ipt in form.find_all('input'):
            if ipt['type'] in ('button', 'submit') or ipt.get('name') is None:
                continue

            valmap[ipt['name']] = ipt.get('value') or ''


        fn = fnmap.get(up.hostname)
        if fn is not None:
            print(f"Passing on to unsubscribe function: {fn}")
            return fn(url, baseurl, resp.text, form, valmap)

        else:
            print(f"Pulling params out of form:\n\n    {form.attrs}\n")
            submit = form.get('action')
            print(f"Raw form submit action: '{submit}'")

            if submit is None:
                print("Cannot automatically submit unsubscribe form. Skipping")
                return False

            elif len(submit) < 1:
                submit = url
            
            elif submit.startswith('/'):
                    submit = baseurl + submit

            elif not submit.startswith('http'):
                parts = urlpath.split('/')[0:-1]
                submit = '/'.join(parts) + '/' + submit

            method = form.get('method') or 'POST'

            formstr = "\n- ".join([f"{k} = {valmap[k]}" for k in valmap])
            print(f"Submit {method} to: {submit} with form values:\n\n- {formstr}")

            try:
                if method.upper() == 'POST':
                    resp = requests.post(submit, params=valmap)
                else:
                    resp = requests.get(submit, params=valmap)

                print(f"Unsubscribe form result: {resp.status_code}")
                return resp.status_code == 200
            except Exception as e:
                print(f"Failed to send HTTP request for unsubscribe: {str(e)}")

            return False
    else:
        return True

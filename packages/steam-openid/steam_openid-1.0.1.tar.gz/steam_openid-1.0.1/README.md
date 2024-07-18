# steam-openid

steam-openid is a Python wrapper for handling Steam OpenID authentication using the `python3-openid` library.

## Requirements

- Python 3.6 or higher
- python3-openid

You can install the required dependencies with:

```bash
pip install -r requirements.txt
```

## Example usage
```python
steam_openid = SteamOpenID(
    realm="http://localhost:8080/steam/login",
    return_to="http://localhost:8080/steam/callback"
)


@app.route("/steam/login")
def login():
    redirect_url = steam_openid.get_redirect_url()
    return redirect(redirect_url)


@app.route("/steam/callback")
def callback(request):
    steam_id = steam_openid.validate_results(request.query_params)
    if steam_id:
        return 200, f"Your steam id is: {steam_id}"
    else:
        return 403, "Failed to authenticate"
```

## Contributions

Pull requests are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.


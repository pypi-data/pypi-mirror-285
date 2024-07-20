# Django-Sheets  
  
Django-GSheets is a library to export data fron Django to Google Sheets  
  
## Installation  
  
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.  
  
```bash  
pip install Django-GSheets-Export
```  
  
## Usage  
  
Add **GOOGLE_APPLICATION_CREDENTIALS_PATH**  key in setup.py  
  
GOOGLE_APPLICATION_CREDENTIALS_PATH point to google credentials file, for more information of how to authenticate   
https://developers.google.com/identity/protocols/oauth2?hl  
https://developers.google.com/identity/protocols/oauth2/service-account  
  

    from django_sheets.gsheets import GoogleSheets  
      
    g = GoogleSheets()  
      
    #Name of spreadsheet  
    g.create(f'{name}') #Name of spreadsheet  
      
    # Fill spreadsheet with data  
    g.update_values(data) # Fill spreadsheet with data  
      
    #Share to email user  
    g.share(email)
  
  
  
**data**: must be a Queryset, a dictionary or a list  
  
Queryset and dictionary create a row with titles name.  
  
  
## License  
  
MIT License  
  
Copyright (c) 2024 Nicolas Candela Alvarez  
  
Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  
  
The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.  
  
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.
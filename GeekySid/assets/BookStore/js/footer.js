@import "compass/css3";

@import url(https://fonts.googleapis.com/css?family=Raleway);

/* Colors */

$dk-blue: #555555;
$blue: #333333;
$light-blue: #444444;
$green: #222222;
$social-size: 0.8em;
$social-width: 20%;

* {
  margin: 0;
  padding: 0;
  @include box-sizing(border-box);
}

html, body {
  font-family: Raleway, sans-serif;  
  background-color: #fff;
}

footer {
  width: 100%;
  display: inline-block;
  margin: 2em 0;
  height: 70px;
  background-color: #000;
  .copyright {
    width: 50%;
    float: left;
    @media (max-width: 600px) {
      width: 100%;
    }
    p {
      padding-left: 10%;
      color: white;
      font-size: 0.7em;
      line-height: 70px;
      text-transform: capitalize;
      letter-spacing: 1px;
      @media (max-width: 600px) {
        text-align: center;
        padding: 0;
      }
    }
  }
  .social {
      width: 50%;
      float: right;
    @media (max-width: 600px) {
      width: 100%;
    }
     a {
      float: left;
      line-height: 70px;
      text-decoration: none;
      color: white;
      text-align: center;
      font-weight: bold; 
      @include transition(all, 0.3s);
       &:hover {
         background-color: #222;
         @include transition(all, .3s);
       }
    }
  }
}

.linked {
  background-color: $dk-blue;
  font-size: $social-size;
  width: $social-width;
}

.face {
  background-color: $blue;
  font-size: $social-size;
  width: $social-width;
}

.tweet {
  background-color: $light-blue;
  font-size: $social-size;
  width: $social-width;
}

.support {
  background-color: $green;
  font-size: $social-size;
  width: 40%;
}


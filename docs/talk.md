---
marp: true
---

<!-- footer: ![w:150](LDF_logo.png) -->

<style>
section {
  place-content: flex-start;
  background-color: #FAFAFA;
  padding: 30px !important;
}

h1 {
  color: #0a5028;
}

footer {
  left: auto;
  right: auto;
  top: auto;
  bottom: auto;
  right: 0px;
  bottom: 0px;
}

.box-adv {
  background:#e8f5e9; 
  border-left:6px solid #2e7d32; 
  padding-top:.5em; 
  padding-bottom:.5em; 
  margin:1em 0;
}

.box-lim {
  background:#fdecea; 
  border-left:6px solid #c62828; 
  padding-top:.5em; 
  padding-bottom:.5em; 
  margin:1em 0;
}

section.title {
  place-content: center;
  padding: 80px !important;
}

</style>

<!-- _class: title -->

![bg left](strom.png)
# When acoustic tomography meets resistograph

Robert Mařík & Valentino Cristini  
Mendel University in Brno

---

<!-- _class: title -->

![bg left](strom.png)

# Content of the talk

- Tomograph and resistograph: strengths and limitations
- Combined approach: a Python library to merge data from both devices
- Vibe coding (ChatGPT)
- Code containerization (Docker)

---

# Tomograph

- Fast and reliable tool for stem inspection  
- Provides **global information** across the whole cross section  
- Shows size and shape of internal defects  

<div class="box-lim">

- Limited by wave length and number of rays for reconstruction  
- Cracks are reported as cavities  

</div>

![bg left](tree05.png)

---

# Resistograph

- Measures the power required for microdrilling at a fixed speed  
- Provides **local** mechanical properties of the material  

![](resistograph_curves.png)

---

![bg left:60% width:100%](resistograph_2D.png)

# Data in cross section geometry

- Transform resistograph data into 2D cross-section geometry  
- Visualize the transformed data  
- Two types of visualization
  - curves
  - color scale

---

![bg left height:100%](resistograph_over_tomo.png)

# Merge data

- Merge resistograph data with tomograph data  
- Visualize merged datasets  
- Long dark part: cavity  
- Short dark part: crack or small cavity  

---

# Python library

![bg left:60% height:100%](overlays.png)

## Advantages

<div class="box-adv">

- Python is widely used in scientific data processing  
- Easy automation, scaling, modification, sharing, and reuse  
- Simple integration with other tools  

</div>

---

# Python library

![bg left:60% width:100%](python_code.png)

## Limitations

<div class="box-lim">

- No graphical user interface (GUI)  
- Requires programming skills  
- Needs installation of Python, IDE, and libraries  

</div>

---

![bg left:60% ](app2.png)

# Streamlit

<div class="box-adv">

- Library for building interactive web apps  
- Requires minimal code  
- Provides interactive widgets for user input  
- Real-time updates  
- Widely used in data science and machine learning  

</div>

---

![bg left:60%](app2.png)

# Vibe coding

- Programming with large language models  
- ChatGPT 5 (August 2025)  
- Web app produced in two prompts  

~~~
I have the following library. Write 
a streamlit program that allows you 
to upload a zipped directory with data 
and run commands corresponding to 
the main function on it. 
The output will be displayed.
~~~

~~~
OK. I want to be able to change 
the preset options in the left panel.
~~~

---

![bg left:50%](docker.png)

# Docker

- Containerization platform  

<div class="box-adv">

- Packages app and dependencies into a single container  
- Ensures consistency across environments  
- Easy to share and deploy  
- Widely used in industry and research  

</div>

---

![bg left:50%](docker.png)

# Run dockerized app

~~~
docker compose up
~~~

<div class="box-adv">

- No Python install required  
- No dependency issues  
- Works on Win / Mac / Linux  
- Just clone repo with `Dockerfile` and `docker-compose.yml`  
- First run takes minutes, later runs take ms  

</div>

---

![bg left](strom2.png)

# Summary

- Resistograph and tomograph are complementary tools for tree stem inspection  

<div class="box-adv">

- A Python library was developed to simplify data interpretation  
- GUI is possible with Streamlit  
- Installation can be simplified and repeated with Docker  

</div>

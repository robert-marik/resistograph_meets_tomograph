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
  background: #e8f5e9; 
  border-left:6px solid #2e7d32; 
  padding-top:.5em; 
  padding-bottom:.5em; 
  margin:1em 0;
}

.box-lim {
  background: #fdecea; 
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
- Combined approach: a Python library for simultaneous interpretation 
- Vibe coding (ChatGPT)
- Code containerization (Docker)

---

# Acoustic tomograph

- Tool for fast stem inspection  
- Provides **global information** across the whole cross section  
- Green part - high sound speed value - sound wood
- Shows size and shape of internal defects  

<div class="box-lim">

- Limited by long wavelength and small number of rays for reconstruction  
- Cracks are reported as cavities  

</div>

![bg left](tree05.png)

---

# Resistograph

- Measures the power required for microdrilling at a fixed speed  
- Provides **local** mechanical properties of the material  
- Note short(!) valleys: the central cavity hypotheses is not accepted
- Projection of the data to the stem cross section would reveal details of the defect

![](resistograph_curves.png)

---

![bg left:60% width:100%](resistograph_2D.png)

# Data in cross section geometry

- Transform resistograph data into 2D cross-section geometry  
- Two types of visualization
  - curves
  - color scale
- Written as Python library
- Published on GitHub

---

![bg left height:100%](resistograph_over_tomo.png)

# Merge data

- Resistograph data in a tomogram  
- Increases the accuracy of data interpretation
- The dark strips allow to localize the defect
- In our case the hypotheses have been confirmed by detailed inspection after felling the tree

---

# Python library

![bg left:60% height:100%](overlays.png)

## Advantages

<div class="box-adv">

- Python is widely used in scientific data processing  
- Easy automation, scaling, modification, sharing, and reuse  
- Simple [integration](https://robert-marik.github.io/resistograph_meets_tomograph) with other tools  

</div>

---

# Python library

![bg left:60% width:100%](python_code.png)

## Limitations

<div class="box-lim">

- Needs installation of Python ecosystem  
- Requires programming skills  
- No graphical user interface

</div>

---

![bg left:60% ](app2.png)

# Streamlit

<div class="box-adv">

- Library for building interactive web apps  
- GUI in web browser
- Widely used in industry and academia
- Requires minimal code  

</div>

---

![bg left:60%](app2.png)

# Vibe coding

- Code written by AI (LLM)
- ChatGPT 5 in August 2025
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

<div class="box-adv">

- Packages app and dependencies into a single container  
- Ensures consistency across environments  - ideal for **transparent and repeatable data processing**
- Widely used in industry and academia

</div>

- In some fields, the "compute capsule" is submitted together with the manuscript (Code Ocean).


---

![bg left:50%](docker.png)

# Run dockerized app

~~~
docker compose up
~~~

<div class="box-adv">

- First run takes minutes, later runs take ms
- No Python install required  
- No dependency issues  
- Works on Win / Mac / Linux  

</div>


---

![bg left](strom2.png)

# Summary

- Resistograph and tomograph are complementary tools for tree inspection  

<div class="box-adv">

- A Python library was developed to enhance data interpretation  
- GUI is possible with Streamlit
- Coding can be done with AI support
- Installation can be simplified and repeated with Docker  

</div>

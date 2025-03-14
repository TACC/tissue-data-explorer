---
title: 'Tissue Data Explorer: a website template for presenting tissue sample research findings'

tags:
  - Python
  - biology
  - spatial biology
  - microscopy
  - anatomy
  - transcriptomics
  - histology
  - proteomics
  - 3D models

authors:
  - name: James A. Labyer
    orcid: 0009-0003-8222-2079
    affiliation: 1
  - name: Erik Ferlanti
    orcid: 0000-0001-5128-1584
    affiliation: 1
  - name: Martha Campbell-Thompson
    orcid: 0000-0001-6878-1235
    affiliation: 2
  - name: Clayton E. Mathews
    orcid: 0000-0002-8817-6355
    affiliation: 2
  - name: Wei-Jun Qian
    orcid: 0000-0002-8817-6355
    affiliation: 3
  - name: James P. Carson
    orcid: 0000-0001-9009-5645
    affiliation: 1
affiliations:
  - name: Texas Advanced Computing Center, The University of Texas at Austin, Austin, TX
    index: 1
  - name: Department of Pathology, Immunology and Laboratory Medicine, University of Florida, Gainesville, FL
    index: 2
  - name: Biological Sciences Division, Pacific Northwest National Laboratory, Richland, WA
    index: 3
date: 21 February 2025
bibliography: paper.bib

---

# Summary

The Tissue Data Explorer is a Python code repository that can be used to stand up a website for displaying 2D and 3D biomolecular datasets that have been collected from tissue samples taken from organs [@Labyer:2025]. The Tissue Data Explorer includes interfaces for loading and displaying image stacks, spatial maps of measurements taken from different areas within the tissue sample, 3D models of the tissue sample, and links to custom reports. Life sciences researchers can stand up an instance of the website as is, or they can fork the repository and modify the interfaces to accommodate additional data types. To enable easier customization, the website is written using the Plotly Dash visualization framework [@Parmer:2024]. Dash allows users to build visuals using Python, which is likely to be easier for many biologists because Python knowledge is common among life sciences researchers [@Mariano:2020] [@Boudreau:2021]. This is in contrast with other common web languages like JavaScript, which is popular among software developers [@Stack:2024] but has not achieved the same level of adoption with life sciences researchers [@Sorani:2012].

# Statement of Need

This software emerged from a project which aimed to provide interactive visualization of data collected by a Human BioMolecular Atlas Program  (HuBMAP) [@Jain:2023] pancreas Tissue Mapping Center to facilitate exploration of the datasets via web-browser. We realized that other research teams have collected or will collect similar data sets on other types of tissue, and may also want to provide interactive visualizations of their own datasets. While there do exist large, centralized websites that host biology datasets and provide users with interactive data analysis capabilities [@Börner:2022], these other services do not provide researchers wide control over how the data is displayed. Our software gives researchers display interfaces out of the box, but also provides a model for how researchers may create other visualizations as they see fit for their own needs. While we developed this software for a future publication of pancreas data, we present here the Tissue Data Explorer along with provided synthetic sample data. 

# Main Features

The software package consists of:

- a configuration app, which requires authentication and allows deployers to upload the data that will display on the website
- a display app, which provides an interactive display for the data and allows viewers to download the source data files

## Volumetric Map
The display app includes the ability to visualize molecular spatial data collected throughout a 3D volume grid. The tool provides four different visualization modes for the volume grid so that researchers can easily visualize the magnitude of the molecular measurements taken across the tissue sample, including interior measurements. The volumetric map can display multiple different measurements, and can filter the tissue sample by layer or by inclusion in a category. Users can also adjust the color scheme and opacity of the visualizations.

![Visualizing synthetic data using the volumetric map interface. Insets show different selectable visualization modes. \label{fig:volumetric-map}](volumetric-map.png)

## 3D Models
The display app can display 3D models of a tissue sample or organ. Multiple 3D models can be loaded together to display a set of regions. When a user hovers over an object, the application displays the coordinates of the point and the name of the object. When a user clicks on an object that is identified as a sample block, the app displays additional information about the block in the gray panel on the right-hand side of the model.

![An interactive 3D model of an example synthetic tissue structure (orange sphere) with sample tissue blocks shown in blue. When selecting a specific block, the link to the data collected from that block is provided. \label{fig:3d}](3d.png)

## Image Stack Viewer
The display app also handles image stacks. Image stacks are loaded into the app as a series of .PNG files along with the source files. The .PNGs are used for the website display and the source files are made available for download. All image sets that are available for a tissue block are listed together, and users can click an image set to view and download the images. The .PNG images are displayed with a slider that allows users to scroll through the images.

![Image sets associated with a tissue block.\label{fig:sci-img}](imgs-list-short.png)

![Interface for exploring a multichannel stack of images, shown here with a synthetic image stack.\label{fig:sci-img}](sci-img.png)

## Report Links
If the researchers have additional reports, such as Bioconductor HTML-based reports [@Huntley:2013], that are hosted elsewhere, they can configure links to those reports from within the app.

## Data Upload
The volumetric map data, 3D models, image stacks and source files, and report links can all be uploaded to the display site using the configuration site. The configuration site validates the uploaded data before moving it into a shared location for the display site to access. The configuration site also provides downloads for example files that describe the required formats for the data.

![The configuration portal.\label{fig:config-portal}](config-portal.png)

# Technical Design

The project is containerized using Docker [@docker], which facilitates website setup because users can run a copy of the website without manually installing and managing the software dependencies [@Ferlanti:2023]. The display site and configuration site are deployed with separate Docker containers that both point to a shared Docker volume, where the configuration site publishes validated data for display by the display site. The two sites are independent, so the configuration site can be taken down once the researchers have completed loading their data.

If the researchers are satisfied with the existing interfaces, they can stand up a functional website without writing any new code. Both sites are written in Python with Plotly Dash, which provides a Flask server and wraps React components in Python. This allows developers to build interactive data visualizations without writing any JavaScript, so if researchers want to add new interfaces to their version of the site they can do so in Python.

# Acknowledgements

We thank the Texas Advanced Computing Center (TACC) staff and the National Science Foundation (NSF) Leadership Class Computing Facility (LCCF) Internship Program for supporting James Labyer and this work. We also thank the National Institutes of Health Common Fund's HuBMAP program and National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK) project 5U54DK127823 and its team members for the feedback and datasets that shaped the development of this software.

# References

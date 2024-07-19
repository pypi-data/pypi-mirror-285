# mukesh

A simple package to process aerial images and generate orthophotos.

## Installation

pip install mukesh


## Prerequisites

Ensure you have Docker installed and running on your system. You can install Docker from [here](https://www.docker.com/get-started).

## Usage


from mukesh import process_images

image_folder = '/path/to/images'
output_dir = '/path/to/output'
process_images(image_folder, output_dir)

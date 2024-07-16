# Coding Project: MNIST digits sequence generator

The goal of this project is to write a Python package that can generate images
representing sequences of numbers, for data augmentation purposes.

These images would be used to train classifiers and generative deep learning
models. A script that saves examples of generated images is helpful in
inspecting the characteristics of the generated images and in inspecting the
trained models behaviours.

## Specifications

Please use Python. As a starting point, you may use images representing each
digit from the [MNIST database](http://yann.lecun.com/exdb/mnist/)
([mirror](https://data.deepai.org/mnist.zip)), and process the files
coming from this website using your own code.

To generate an image of a sequence, the digits have to be stacked horizontally
and the spacing between them should follow a uniform distribution over a range
determined by two user specified numbers. Make sure to take the padding present
in the digit images into account. The numerical values of the digits
themselves are provided by the user and each digit in the generated sequence is
then chosen randomly from one of its representations in the MNIST dataset.
To look more realistic, the images should have black text on a white background.

The width of the output image in pixels is specified by the user, while the
height should be 28 pixels (i.e. identical to that of the MNIST digits). The
code should contain both an API and two CLIs.

The function should look as follows:

```python
# A single function defined as follows:
def generate_numbers_sequence(digits: Iterable[int], spacing_range: Tuple[int, int], image_width: int) -> np.ndarray:
    """
    Generate an image that contains the sequence of given numbers, spaced
    randomly using a uniform distribution.

    Parameters
    ----------
    digits:
	An iterable containing the numerical values of the digits from which
        the sequence will be generated (for example [3, 5, 0]).
    spacing_range:
	a (minimum, maximum) int pair (tuple), representing the min and max spacing
        between digits. Unit should be pixel.
    image_width:
        specifies the width of the image in pixels.

    Returns
    -------
    The image containing the sequence of numbers. Images should be represented
    as floating point 32bits numpy arrays with a scale ranging from 0 (black) to
    1 (white), the first dimension corresponding to the height and the second
    dimension to the width.
```

The first script, installed as `generate-numbers-sequence`, acts as a low-level
command line interface for the above API. The script is expected to use the
above API, and accept the following parameters:

* sequence: the sequence of digits to be generated
* min spacing: minimum spacing between consecutive digits
* max spacing: maximum spacing between consecutive digits
* image width: width of the generated image
* output path: where to store the generated image, current directory by default

The generated image is saved as `.png`.

The second CLI command, installed as `generate-phone-numbers`, is used to
generate a dataset of images containing random sequences looking like Japanese
phone numbers. All sequences should be unique and the script should accept the
following parameters:

* min spacing: minimum spacing between consecutive digits
* max spacing: maximum spacing between consecutive digits
* image width: width of the generated images
* num images: number of images to generate
* output path: where to store the generated images

Note that besides these interfaces, you are free to implement the package as
you wish.

If you have time, you may also want to expand the project with, for example:
- additional methods for data expansion (warping, noise, etc.)
- other image datasets
- model training on the generated images

It is expected that some of the problems have multiple reasonable solutions: in
this case, you should be ready to answer questions about the tradeoffs.
Ideally, you would document them in your README file.

## What should be provided

* a pip-installable Python package that defines the main function, which can
  be imported with `from number_generator import generate_numbers_sequence`.
* a README file explaining how to install the package, how to use it, and
  discussing tradeoffs and implementation details.

We expect the code to be organized, extensible, designed, tested and documented
as if it were going into production.
Make sure everything works correctly in an isolated environment (e.g. Docker,
fresh virtualenv, ...).

Please submit the work assignement as a zipfile or tarball containing your git
repository (with the .git folder). Make sure it is not put in a public place!

## Scoring

We value quality over feature-completeness. It is fine to leave things aside
provided you call them out in your project's README. Part of the goal of this
exercise is to help us identify what you consider production-ready code.

We will look at the following to assess your code:

* Clarity: Is the code organized in well defined functions, with separated
  concerns? Is it implemented in a way that makes it difficult or simple to
  extend? Depending on your advertised Python expertise, we will also look
  whether the code is idiomatic Python.
* Documentation: Does the README clearly and concisely explain the problem and solution?
  Are technical tradeoffs explained?
* Testing and correctness: The code needs to do what is asked, and you need to be able to
  explain why it is correct. Ideally, the code would have some tests. We're not
  looking for full coverage (given time constraint) but just trying to get a
  feel for your testing skills.
* Automation: How easy to run and reproducible are the installation, scripts and
  tests?
* Technical choices: Do choices of libraries, architecture etc. seem appropriate for the
  chosen application?
* Going the last mile: If you find the problem trivial, can you think of more
  advanced data augmentation techniques for the problem of handwritten digit
  recognition? Something else you think might be useful to train a model on this
  data?

Good luck!

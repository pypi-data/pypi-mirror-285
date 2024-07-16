#####
Clipp
#####

.. The shorthand for line blocks doesn't render properly on github, so we are forced to use the line-break substitution.

| **Latest Version:** 1.3.2
| **Status:** Beta, active development

Clipp is a POSIX-compliant, CLI parser library for building command-line interfaces, designed to be flexible, intelligent, and uncompromisingly simple. The package is similar to argparse but aims to be more intuitive and less cumbersome. Clipp allows for greater code re-use than argparse and is much more scalable. In terms of parser latency, clipp typically outperforms argparse. Though clipp is much more minimalist than argparse, its API has most of the features you would expect to find in a command-line parsing library.

.. contents:: Table of Contents

Documentation
=============

Up-to-date API documentation can be found here: `<https://jammin93.github.io/clipp/>`_

Features
========

- A simple and intuitive API.
- Support for both positional and non-positional options, as well as flags.
- Option groups allow for greater code re-use and flexibility.
- Supports mutually exclusive and dependent options.
- Supports option escaping with double-dash (--) out of the box.
- Allows for nested sub-commands.
- Automatic help and usage formatting.
- Automatic handling of command-line syntax errors.
- Supports post-processing of option arguments via callback functions.
- Easily override defaults for help and version info options.

Installation
============

.. code:: console

	$ python -m pip install clipp

Quickstart
==========

Let's start by creating a file called **sum.py**, which we will use to sum a sequence of integers.

.. code:: python

	from clipp import Command

	command = Command()

By default, the name of the command is the name of the script which defines the command object. Adding options to the command is easy. For those familiar with argparse, some of the code below should seem familiar. Nevertheless, although syntactically similar, clipp does not behave identically to argparse. For instance, the ``action`` argument seen below plays a much different role in clipp's API. It accepts a callable which is used for post-processing the argument tokens collected for that option. The ``dtype`` (data type) argument, by contrast, is clipp's equivalent of argparse's ``type`` argument, and serves the same purpose.

.. code:: python

	...

	command.add_parameter(
		"integer",
		quota="*",
		dtype=int,
		action=sum,
		dest="value",
		help="An integer value.",
	)

Clipp refers to positional options as parameters rather than options because users are typically required to supply arguments to positional options. They are, therefore, not *typically* optional. The asterisk (``*``) supplied above is a greedy operator which represents a "zero-or-more" quota and is one exception to this rule. Parameters with zero-or-more quotas are technically optional because the parser is permitted to consume zero arguments. By contrast, the other greedy operator which may be supplied to ``quota`` is the plus character (``+``). It represents "one-or-more". Unlike parameters with zero-or-more quotas, parameters with quotas of one-or-more are not optional.

.. admonition:: **Note**

	Throughout this documentation, the term "option" will be used wherever differentiation between options and parameters is not critical. In cases where a distinction should be made, parameters will be referred to by their formal name.

The parameter we have defined above accomplishes a few things: it tells the parser to consume a list of strings which are expected to represent integer values; convert those strings to type ``int``; compute the sum of those values; and map the sum to the key "value" in the namespace object which the parser returns.

Let's get familiar with how to parse arguments from the command-line.

.. code:: python

	...

	if __name__ == "__main__":
		processed = command.parse()

.. code:: console

	$ python3 -m sum --help
	Usage: sum <integer>... [--help]

	Positional Arguments:
	integer               An integer value.

	Options:
	--help, -h            Display this help message.

The default help option is an example of a fast flag. When the parser encounters an argument token which represents a valid alias for any of its fast flags, it calls the corresponding flag's callback function and then forces the script to terminate with an exit code of zero. By default, the help option's callback function prints the command's help message to the terminal.

Now that we have a better understanding of our command's syntax, let's add a line for output to our utility and then have a go at summing a few integers.

.. code:: python

	...

	print(processed)

.. code:: console

	$ python3 -m sum 1 2 3
	Namespace(globals={}, locals={'sum': {'value': 6}}, extra=[])

The namespace object returned by the parser is a ``namedtuple`` which has three fields: ``globals``, ``locals``, and ``extra``. The ``globals`` field contains all options which are global and are therefore recognized by all commands in the command hierarchy. The ``locals`` field is a dictionary containing each of the commands encountered by the parser, and ``extra`` is a list of all positional arguments which were not consumed by the parser. Each of the nested dictionaries in ``locals`` contains that command's options, mapped to their corresponding values. In this case, we can see that the computed value for the parameter "integer" was mapped to its destination key (``dest``) which is "value".

Surely, most utilities will be more feature-rich than the utility we have written. Let's add some more functionality to our utility.

.. code:: python

	...

	command.add_option(
		"--mod", "-m",
		dtype=int,
		const=2,
		help="Compute the sum mod N, where N is a valid integer.",
	)

	if __name__ == "__main__":
		processed = command.parse()
		print(processed)

.. code:: console

	$ python3 -m sum --help
	Usage: sum <integer>... [--help] [--mod=<arg>]

	Positional Arguments:
	integer               An integer value.

	Options:
	--help, -h            Display this help message.
	--mod, -m             Compute the sum mod N, where N is a valid
	                      integer.
	$ python3 -m sum 1 2 3 --mod
	Namespace(globals={}, locals={'sum': {'value': 6, 'mod': 2}}, extra=[])


In the command-line example above, we see that "--mod" now appears in the locals dictionary under "sum" (our command). Since no argument was supplied to "--mod", its value is equal to that of the ``const`` argument which we passed in the ``add_option`` method. The value of ``const`` is the value used by the parser when an option IS encountered but no arguments are received. The counterpart to the ``const`` argument is ``default`` which represents the value used by the parser whenever an option is NOT encountered at the command-line. Whether an option supports ``default`` or ``const`` is ultimately determined by its quota.

.. admonition:: **Note**

	For non-positional options, ``default`` and ``const`` are NOT supported if the parser expects to consume one, **or more**, argument tokens (i.e. ``quota`` > 1 or ``quota`` == "+"). For parameters, ``default`` and ``const`` are **only** supported for zero-or-more quotas (*).

A good use-case for an option which utilizes a default is a flag. Flags always have a ``quota`` of zero and therefore do not expect any arguments. Their possible values are predetermined by ``const`` and ``default``.

.. code:: python

	...

	command.add_flag(
		"--hexify",
		const=True,
		default=False,
		help="Convert the result to hexidecimal".,
	)

	if __name__ == "__main__":
		processed = command.parse()
		print(processed)

.. code:: console

	$ python3 -m sum 1 2 3 --hexify
	Namespace(globals={}, locals={'sum': {'value': 6, 'hexify': True}}, extra=[])

Notice that the values used above are boolean values, and the flag we have added ultimately represents a binary option. Clipp has a convenience method for binary flags. Let's adjust the code above and use the ``add_binary_flag`` method instead.

.. code:: python

	...

	command.add_binary_flag(
		"--hexify",
		help="Convert the result to hexidecimal.",
	)

	...

.. code:: console

	$ python3 -m sum 1 2 3 --hexify
	Namespace(globals={}, locals={'sum': {'value': 6, 'hexify': True}}, extra=[])

By default, the ``const`` argument of the method ``add_binary_flag`` is set to ``True``, and ``default`` is always the opposite of ``const``.

A flag, however, may not be the best choice. Perhaps we want to allow users to select a particular result type. We can adjust the above code once more.

.. code:: python

	...

	command.add_option(
		"--result-type", "-t",
		choices=["hex", "bin"],
		help="Convert the result to either hexidecimal (hex) or binary (bin).",
	)

	...

.. code:: console

	$ python3 -m sum --help
	Usage: sum <integer>... [--help] [--mod=<arg>]
               [--result-type=<bin|hex>]

	Positional Arguments:
	integer               An integer value.

	Options:
	--help, -h            Display this help message.
	--mod, -m             Compute the sum mod N, where N is a valid
	                      integer.
	--result-type, -t     Convert the result to either hexidecimal (hex)
	                      or binary (bin).
	$ python3 -m 1 2 3 -t bin
	Namespace(globals={}, locals={'sum': {'value': 6, 'result_type': 'bin'}}, extra=[])

At this point, our utility isn't very useful for the end-user. We'll need to make sure that our utility does what it claims if we want happy users.

.. code:: python

	def compute_result(options: dict) -> str:
		value = options["value"]
		if "--mod" in options:
			value = value % options["--mod"]

		if "--result-type" not in options:
			value = str(value)
		elif options["--result-type"] == "hex":
			value = hex(value)
		else:
			value = bin(value)

		return value

	if __name__ == "__main__":
		processed = command.parse()
		result = compute_result(processed.locals["sum"])
		print(result)

.. code:: console

	$ python3 -m sum 3 7 9
	19
	$ python3 -m sum 3 7 9 --mod=4
	3
	$ python3 -m sum 3 7 9 -t bin
	0b10011

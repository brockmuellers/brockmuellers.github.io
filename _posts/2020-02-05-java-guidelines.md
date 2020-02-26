---
# https://github.com/3Scan/kesm/pull/4658/files
layout: post  
title:  "Guidelines for Java development"
subtitle: "(and why you should make your own)"
image: /assets/images/snowy_railing.jpg
categories: software
---

At a previous job, I collected an incomplete set of "best practice" guidelines for Java developers on the team. I had three reasons for doing this:

1. I made a lot of mistakes when first learning Java, and wanted to prevent others from falling in the same traps.

2. Some junior developers were starting to work on the Java codebase, and I ended up repeating a lot of the same advice in code reviews.

3. Everyone had differing opinions. That's quite fine, but getting everyone to agree on a "correct" way of doing things leads to a much cleaner codebase. This required quite a bit of compromise, but it reduced friction afterwards.

I started out with scattered list of contentious points and common mistakes. I talked through the difficult points with other people, got reviews from interested parties, and put the final result in our developer docs. It was easy to direct developers to it when needed, and easy to append new points we wanted to specify.

### Why should you do this too?

It's important for a software team to have agreed-upon guidelines like these, whether codified or not. Clearly there's benefit to sharing knowledge of common mistakes. Code reviews get easier - less nitpicking required. It also keeps the peace. A team can spend endless time [bikeshedding](https://en.wikipedia.org/wiki/Law_of_triviality), returning to the same issues repeatedly, never leaving anyone happy. Instead, you can make the controversial decisions once and leave it at that.

Doing this allows the whole team to own the code. Codebases become difficult to read when everyone writes code according to their own preference. It’s difficult to predict where things are defined and reason about behavior. And it’s never comfortable to fiddle around with a class that someone else wrote in their own style.

This obviously should be a living document, in a team wiki or something similar. Making it easy to edit keeps it relevant to your ever-changing team and product.

As a side note: a great way to reduce the number of guidelines you need is to implement a style guide (for example, the [Google style guide](https://google.github.io/styleguide/javaguide.html)). It takes basically no effort to follow it if you use a formatter like [Spotless](https://github.com/diffplug/spotless). Similarly, you can use a static analysis tool like [Error Prone](https://github.com/google/error-prone) to prevent people from committing certain classes of mistakes. I'll also point out the [Oracle Java Tutorial](https://docs.oracle.com/javase/tutorial/) as a great resource for Java beginners.

***

With that, here are the guidelines that we used (edited a bit to be less domain-specific).

### Performance

Write for readability over performance. The reason for this is two-fold:

1. The JVM JIT compiler is magic. In many cases, it can optimize your code better than you will, through branch predictions, loop unrolling, inlining methods, allocation elimination, lock elision, and much, much more.

2. Most performance “optimizations” implemented by the programmer have a very minimal effect, especially given the aforementioned compile optimizations. Writing for readability will likely save more time than the programmer’s optimization. This is both time spent by engineers trying to understand the code, and time spent chasing down obscure bugs.

Obviously there will be some complex situations when this guideline does not hold. Use your best judgement.

### Exceptions

*  Use checked exceptions (ex. `IOException`, `InterruptedException`) for recoverable errors, and unchecked exceptions (ex. `RuntimeException`, `AssertionError`, `NullPointerException`) for unrecoverable errors. Both types of exceptions should have clear and descriptive messages.

* Checked exceptions should be specific. In many cases it is useful to create a domain-specific checked exception.

* Do not catch unchecked exceptions. Their role is not to be caught, it is to kill the program loudly. The exception to this is when programming external-facing APIs, where there may be certain expected behavior in the case of an exception.

### Documentation

Public methods and classes should always have a docstring that describes their role, expectations, and edge-case behavior. The format for this is often made clear in style guides. Documentation for simple getters and setters is not necessary. Document any private methods and classes if it will be useful for the reader.

### Safety

* Be careful with mutable class fields. Use immutable types when possible. Do not provide outside callers direct references to the field — return a copy, if practical. Encapsulate any mutation inside class methods, and consider what happens if multiple callers are simultaneously calling these methods.

* Do not write fun and tricky logic. Boring logic is easy to test and easy to trust. If your logic is fun, separate it into boring and individually-tested pieces.

* Handle nulls explicitly. If a field or argument may be null, use the javax `@Nullable` annotation to make the intention crystal clear.

* Consider wrapping common calls to external libraries if they have undesirable, unpredictable, or poorly defined behavior. Common examples of this in Java can be found in OpenCV and the AWS SDK. This can save you from debugging the same issue repeatedly — put the messy library call in a method, test its behavior, catch exceptions and validate input as needed, and use that method in the future. And remember — if these methods aren’t easily discoverable and useable, or if the rest of the team finds them unnecessary, putting time into building a wrapper will be a waste.

### Collections

[This seems like a silly thing to talk about at length, but we worked with a number of collections that needed almost the same interface/behavior as native Java collection types. There were weeks of heated debate over the correct approach to this, so we came to a decision and codified it. No one was quite happy, but it stopped being an issue.]

Do not extend native Java collection types (e.g. `HashMap`, `ArrayList`). It is very difficult to ensure that the new object will behave as expected when treated as the base type. Extending collection types is standard practice in some other languages, but Java programmers generally discourage it.

For simple data storage, an alternative is to store your desired collection as an attribute of another object. If you want to expose the collection methods, delegate them. If you want custom methods for your collection, you can write them on your outer class.

In more complex situations, consider implementing a collection interface (like `Map` instead of `HashMap`). This forces you to write all of your class’s methods, which makes behavior more predictable. (This strategy is an example of using the [composition over inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) principle.)

### Asynchronous code

For asynchronous code, use `CompletableFuture`s. They allow async computation to be performed without blocking a thread. One common use case is when making network calls, which involve dead time spent waiting for responses. There are admittedly drawbacks to `CompletableFuture`s, but using them everywhere allows us to chain asynchronous callbacks, and more easily reason about async processes.

### General software principles

* Choose [composition over inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) whenever reasonable. In Java, this means implementing interfaces instead of extending base classes. Implementing interfaces allows your classes to guarantee multiple behavioral contracts, instead of being bound to a specific base implementation that is not robust to refactoring.

* Keep classes and methods small. Classes should represent simple entities. Methods should have one job. This is crucial for testing, refactoring, understanding, and maintaining.

* Make class fields private, and provide getters when necessary. This is necessary to encapsulate the logic in a class, so callers are not dependent on the class implementation.

### Readability

* Avoid large blocks of code. Use whitespace to separate tiny, logical chunks of code. (Do not be afraid of whitespace. It is your friend.) Use inline documentation to describe unclear bits of code, but better yet, restructure your code and rename methods/variables until the code is clear.

* Name your classes, fields, and methods descriptively. Auto-complete in an IDE removes the effort involved in using longer names, and clear names are what makes your code human-parseable.

* When writing a piece of code, future readers should not be able to tell what member of the team wrote it. Having an institutionally-consistent codebase allows the whole team to easily read, understand, and alter unfamiliar code.


***

It’s impossible to have a complete list of guidelines — there are whole books written on this subject. However, if there is contention over an issue, or if something keeps tripping people up, it’s valuable to define what to do in that situation in the future.

---

*[Also published in The Startup on medium.com](https://medium.com/swlh/guidelines-for-java-development-6cfa9c28fe7e)*

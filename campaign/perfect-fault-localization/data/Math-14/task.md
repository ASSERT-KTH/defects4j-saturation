Repair a real defect in the Java project Math (Defects4J bug Math-14).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src/main/java
  - test sources       : src/test/java   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - org.apache.commons.math3.fitting.PolynomialFitterTest::testLargeSample

Failure output from the initial test run:

```
--- org.apache.commons.math3.fitting.PolynomialFitterTest::testLargeSample
java.lang.OutOfMemoryError: Java heap space
	at org.apache.commons.math3.linear.BlockRealMatrix.createBlocksLayout(BlockRealMatrix.java:271)
	at org.apache.commons.math3.linear.BlockRealMatrix.<init>(BlockRealMatrix.java:107)
	at org.apache.commons.math3.linear.MatrixUtils.createRealMatrix(MatrixUtils.java:82)
	at org.apache.commons.math3.optim.nonlinear.vector.Weight.<init>(Weight.java:43)
	at org.apache.commons.math3.fitting.CurveFitter.fit(CurveFitter.java:175)
	at org.apache.commons.math3.fitting.CurveFitter.fit(CurveFitter.java:136)
	at org.apache.commons.math3.fitting.PolynomialFitter.fit(PolynomialFitter.java:68)
	at org.apache.commons.math3.fitting.PolynomialFitterTest.testLargeSample(PolynomialFitterTest.java:238)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:50)
	at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
	at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:47)
	at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
	at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:325)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:78)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:57)
	at org.junit.runners.ParentRunner$3.run(ParentRunner.java:290)
	at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:71)
	at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:288)
	at org.junit.runners.ParentRunner.access$000(ParentRunner.java:58)
	at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:268)
	at org.junit.runners.ParentRunner.run(ParentRunner.java:363)
	at junit.framework.JUnit4TestAdapter.run(JUnit4TestAdapter.java:38)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
```

Classes the defect is known to be located in:

  - org.apache.commons.math3.optim.nonlinear.vector.jacobian.AbstractLeastSquaresOptimizer
  - org.apache.commons.math3.optim.nonlinear.vector.Weight

Your task: find the root cause and fix it in src/main/java, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.

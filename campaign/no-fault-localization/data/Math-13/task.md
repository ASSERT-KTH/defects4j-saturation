Repair a real defect in the Java project Math (Defects4J bug Math-13).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src/main/java
  - test sources       : src/test/java   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - org.apache.commons.math3.optimization.fitting.PolynomialFitterTest::testLargeSample

Failure output from the initial test run:

```
--- org.apache.commons.math3.optimization.fitting.PolynomialFitterTest::testLargeSample
java.lang.OutOfMemoryError: Java heap space
	at org.apache.commons.math3.linear.DiagonalMatrix.getData(DiagonalMatrix.java:204)
	at org.apache.commons.math3.linear.TriDiagonalTransformer.<init>(TriDiagonalTransformer.java:69)
	at org.apache.commons.math3.linear.EigenDecomposition.transformToTridiagonal(EigenDecomposition.java:561)
	at org.apache.commons.math3.linear.EigenDecomposition.<init>(EigenDecomposition.java:122)
	at org.apache.commons.math3.optimization.general.AbstractLeastSquaresOptimizer.squareRoot(AbstractLeastSquaresOptimizer.java:562)
	at org.apache.commons.math3.optimization.general.AbstractLeastSquaresOptimizer.setUp(AbstractLeastSquaresOptimizer.java:508)
	at org.apache.commons.math3.optimization.direct.BaseAbstractMultivariateVectorOptimizer.optimizeInternal(BaseAbstractMultivariateVectorOptimizer.java:239)
	at org.apache.commons.math3.optimization.general.AbstractLeastSquaresOptimizer.optimizeInternal(AbstractLeastSquaresOptimizer.java:496)
	at org.apache.commons.math3.optimization.general.AbstractLeastSquaresOptimizer.optimize(AbstractLeastSquaresOptimizer.java:423)
	at org.apache.commons.math3.optimization.general.AbstractLeastSquaresOptimizer.optimize(AbstractLeastSquaresOptimizer.java:62)
	at org.apache.commons.math3.optimization.fitting.CurveFitter.fit(CurveFitter.java:189)
	at org.apache.commons.math3.optimization.fitting.CurveFitter.fit(CurveFitter.java:153)
	at org.apache.commons.math3.optimization.fitting.PolynomialFitter.fit(PolynomialFitter.java:110)
	at org.apache.commons.math3.optimization.fitting.PolynomialFitterTest.testLargeSample(PolynomialFitterTest.java:241)
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
```

Your task: find the root cause and fix it in src/main/java, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.

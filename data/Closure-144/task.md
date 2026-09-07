Repair a real defect in the Java project Closure (Defects4J bug Closure-144).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsAssign
  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsMember
  - com.google.javascript.jscomp.CodePrinterTest::testOptionalTypesAnnotation
  - com.google.javascript.jscomp.CodePrinterTest::testTempConstructor
  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsDispatcher1
  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsDispatcher2
  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsImplements
  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsNamespace
  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotations
  - com.google.javascript.jscomp.CodePrinterTest::testVariableArgumentsTypesAnnotation
  - com.google.javascript.jscomp.CodePrinterTest::testEmitUnknownParamTypesAsAllType
  - com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsMemberSubclass
  - com.google.javascript.jscomp.DevirtualizePrototypeMethodsTest::testRewritePrototypeMethods2
  - com.google.javascript.jscomp.DisambiguatePropertiesTest::testStaticProperty
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportDontEmitPrototypePathPrefix
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportMultiple
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportSymbolWithConstructor
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportSymbolDefinedInVar
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportSymbol
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportMultiple2
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportMultiple3
  - com.google.javascript.jscomp.ExternExportsPassTest::testExportProperty
  - com.google.javascript.jscomp.LooseTypeCheckTest::testNestedFunctionInference1
  - com.google.javascript.jscomp.LooseTypeCheckTest::testScoping10
  - com.google.javascript.jscomp.LooseTypeCheckTest::testDuplicateOldTypeDef
  - com.google.javascript.jscomp.LooseTypeCheckTest::testBadConstructorCall
  - com.google.javascript.jscomp.LooseTypeCheckTest::testDontAddMethodsIfNoConstructor
  - com.google.javascript.jscomp.LooseTypeCheckTest::testInterfaceInheritanceCheck11
  - com.google.javascript.jscomp.LooseTypeCheckTest::testErrorMismatchingPropertyOnInterface5
  - com.google.javascript.jscomp.LooseTypeCheckTest::testDuplicateTypeDef
  - com.google.javascript.jscomp.LooseTypeCheckTest::testBug911118
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference12
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference13
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference15
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference16
  - com.google.javascript.jscomp.LooseTypeCheckTest::testPrototypePropertyReference
  - com.google.javascript.jscomp.LooseTypeCheckTest::testGoodExtends7
  - com.google.javascript.jscomp.LooseTypeCheckTest::testTypeRedefinition
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference1
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference2
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference3
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference4
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference7
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference8
  - com.google.javascript.jscomp.LooseTypeCheckTest::testFunctionInference9
  - com.google.javascript.jscomp.LooseTypeCheckTest::testInterfaceInheritanceCheck7
  - com.google.javascript.jscomp.LooseTypeCheckTest::testDuplicateStaticMethodDecl1
  - com.google.javascript.jscomp.LooseTypeCheckTest::testDuplicateStaticMethodDecl5
  - com.google.javascript.jscomp.TypeCheckTest::testNestedFunctionInference1
  - com.google.javascript.jscomp.TypeCheckTest::testScoping10
  - com.google.javascript.jscomp.TypeCheckTest::testDuplicateOldTypeDef
  - com.google.javascript.jscomp.TypeCheckTest::testInferredReturn1
  - com.google.javascript.jscomp.TypeCheckTest::testInferredReturn2
  - com.google.javascript.jscomp.TypeCheckTest::testInferredReturn3
  - com.google.javascript.jscomp.TypeCheckTest::testInferredReturn4
  - com.google.javascript.jscomp.TypeCheckTest::testInferredReturn6
  - com.google.javascript.jscomp.TypeCheckTest::testBadConstructorCall
  - com.google.javascript.jscomp.TypeCheckTest::testDontAddMethodsIfNoConstructor
  - com.google.javascript.jscomp.TypeCheckTest::testInterfaceInheritanceCheck11
  - com.google.javascript.jscomp.TypeCheckTest::testErrorMismatchingPropertyOnInterface5
  - com.google.javascript.jscomp.TypeCheckTest::testDuplicateTypeDef
  - com.google.javascript.jscomp.TypeCheckTest::testBug911118
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference12
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference13
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference15
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference16
  - com.google.javascript.jscomp.TypeCheckTest::testPrototypePropertyReference
  - com.google.javascript.jscomp.TypeCheckTest::testGoodExtends7
  - com.google.javascript.jscomp.TypeCheckTest::testTypeRedefinition
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference1
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference2
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference3
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference4
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference7
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference8
  - com.google.javascript.jscomp.TypeCheckTest::testFunctionInference9
  - com.google.javascript.jscomp.TypeCheckTest::testInterfaceInheritanceCheck7
  - com.google.javascript.jscomp.TypeCheckTest::testDuplicateStaticMethodDecl1
  - com.google.javascript.jscomp.TypeCheckTest::testDuplicateStaticMethodDecl5
  - com.google.javascript.jscomp.TypedScopeCreatorTest::testConstructorNode
  - com.google.javascript.jscomp.TypedScopeCreatorTest::testPropertiesOnInterface
  - com.google.javascript.jscomp.TypedScopeCreatorTest::testMethodBeforeFunction
  - com.google.javascript.jscomp.TypedScopeCreatorTest::testConstructorProperty
  - com.google.javascript.jscomp.TypedScopeCreatorTest::testReturnTypeInference1

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsAssign
junit.framework.ComparisonFailure: expected:</**
 * @[return {undefined}
 * @]constructor
 */
var ...> but was:</**
 * @[]constructor
 */
var ...>
	at junit.framework.Assert.assertEquals(Assert.java:100)
	at junit.framework.Assert.assertEquals(Assert.java:107)
	at junit.framework.TestCase.assertEquals(TestCase.java:269)
	at com.google.javascript.jscomp.CodePrinterTest.assertTypeAnnotations(CodePrinterTest.java:799)
	at com.google.javascript.jscomp.CodePrinterTest.testTypeAnnotationsAssign(CodePrinterTest.java:613)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.TestSuite.runTest(TestSuite.java:252)
	at junit.framework.TestSuite.run(TestSuite.java:247)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
	at org.apache.tools.ant.UnknownElement.execute(UnknownElement.java:291)
	at jdk.internal.reflect.GeneratedMethodAccessor4.invoke(Unknown Source)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.apache.tools.ant.dispatch.DispatchUtils.execute(DispatchUtils.java:106)
	at org.apache.tools.ant.Task.perform(Task.java:348)
	at org.apache.tools.ant.Target.execute(Target.java:392)
	at org.apache.tools.ant.Target.performTasks(Target.java:413)
	at org.apache.tools.ant.Project.executeSortedTargets(Project.java:1399)
	at org.apache.tools.ant.Project.executeTarget(Project.java:1368)
	at org.apache.tools.ant.helper.DefaultExecutor.executeTargets(DefaultExecutor.java:41)
	at org.apache.tools.ant.Project.executeTargets(Project.java:1251)
	at org.apache.tools.ant.Main.runBuild(Main.java:811)
	at org.apache.tools.ant.Main.startAnt(Main.java:217)
	at org.apache.tools.ant.launch.Launcher.run(Launcher.java:280)
	at org.apache.tools.ant.launch.Launcher.main(Launcher.java:109)
--- com.google.javascript.jscomp.CodePrinterTest::testTypeAnnotationsMember
junit.framework.ComparisonFailure: expected:<var a = {};
/**
 * @[return {undefined}
 * @]constructor
 */
a.Fo...> but was:<var a = {};
/**
 * @[]constructor
 */
a.Fo...>
	at junit.framework.Assert.assertEquals(Assert.java:100)
	at junit.framework.Assert.assertEquals(Assert.java:107)
	at junit.framework.TestCase.assertEquals(TestCase.java:269)
	at com.google.javascript.jscomp.CodePrinterTest.assertTypeAnnotations(CodePrinterTest.java:799)
	at com.google.javascript.jscomp.CodePrinterTest.testTypeAnnotationsMember(CodePrinterTest.java:651)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.TestSuite.runTest(TestSuite.java:252)
	at junit.framework.TestSuite.run(TestSuite.java:247)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
	at org.apache.tools.ant.UnknownElement.execute(UnknownElement.java:291)
	at jdk.internal.reflect.GeneratedMethodAccessor4.invoke(Unknown Source)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.apache.tools.ant.dispatch.DispatchUtils.execute(DispatchUtils.java:106)
	at org.apache.tools.ant.Task.perform(Task.java:348)
	at org.apache.tools.ant.Target.execute(Target.java:392)
	at org.apache.tools.ant.Target.performTasks(Target.java:413)
	at org.apache.tools.ant.Project.executeSortedTargets(Project.java:1399)
	at org.apache.tools.ant.Project.executeTarget(Project.java:1368)
	at org.apache.tools.ant.helper.DefaultExecutor.executeTargets(DefaultExecutor.java:41)
	at org.apache.tools.ant.Project.executeTargets(Project.java:1251)
	at org.apache.tools.ant.Main.runBuild(Main.java:811)
	at org.apache.tools.ant.Main.startAnt(Main.java:217)
	at org.apache.tools.ant.launch.Launcher.run(Launcher.java:280)
	at org.apache.tools.ant.launch.Launcher.main(Launcher.java:109)
--- com.google.javascript.jscomp.CodePrinterTest::testOptionalTypesAnnotation
junit.framework.ComparisonFailure: expected:<...param {string=} x
 *[ @return {undefined}
 *]/
var a = function(x...> but was:<...param {string=} x
 *[]/
var a = function(x...>
	at junit.framework.Assert.assertEquals(Assert.java:100)
	at junit.framework.Assert.assertEquals(Assert.java:107)
	at junit.framework.TestCase.assertEquals(TestCase.java:269)
	at com.google.javascript.jscomp.CodePrinterTest.assertTypeAnnotations(CodePrinterTest.java:799)
	at com.google.javascript.jscomp.CodePrinterTest.testOptionalTypesAnnotation(CodePrinterTest.java:753)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.TestSuite.runTest(TestSuite.java:252)
	at junit.framework.TestSuite.run(TestSuite.java:247)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
	at org.apache.tools.ant.UnknownElement.execute(UnknownElement.java:291)
	at jdk.internal.reflect.GeneratedMethodAccessor4.invoke(Unknown Source)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.apache.tools.ant.dispatch.DispatchUtils.execute(DispatchUtils.java:106)
	at org.apache.tools.ant.Task.perform(Task.java:348)
	at org.apache.tools.ant.Target.execute(Target.java:392)
	at org.apache.tools.ant.Target.performTasks(Target.java:413)
	at org.apache.tools.ant.Project.executeSortedTargets(Project.java:1399)
	at org.apache.tools.ant.Project.executeTarget(Project.java:1368)
	at org.apache.tools.ant.helper.DefaultExecutor.executeTargets(DefaultExecutor.java:41)
	at org.apache.tools.ant.Project.executeTargets(Project.java:1251)
	at org.apache.tools.ant.Main.runBuild(Main.java:811)
	at org.apache.tools.ant.Main.startAnt(Main.java:217)
	at org.apache.tools.ant.launch.Launcher.run(Launcher.java:280)
	at org.apache.tools.ant.launch.Launcher.main(Launcher.java:109)
--- com.google.javascript.jscomp.CodePrinterTest::testTempConstructor
junit.framework.ComparisonFailure: expected:</**
 *[ @return {undefined}
 */
var x = function() {
  /**
 * @return {undefined}
 * @constructor
 */
function t1() {
  }
  /**
 * @return {undefined}]
 * @constructor
 */...> but was:</**
 *[/
var x = function() {
  /**
 * @constructor
 */
function t1() {
  }
  /**]
 * @constructor
 */...>
	at junit.framework.Assert.assertEquals(Assert.java:100)
	at junit.framework.Assert.assertEquals(Assert.java:107)
	at junit.framework.TestCase.assertEquals(TestCase.java:269)
	at com.google.javascript.jscomp.CodePrinterTest.assertTypeAnnotations(CodePrinterTest.java:799)
	at com.google.javascript.jscomp.CodePrinterTest.testTempConstructor(CodePrinterTest.java:779)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.TestSuite.runTest(TestSuite.java:252)
	at junit.framework.TestSuite.run(TestSuite.java:247)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
	at org.apache.tools.ant.UnknownElement.execute(UnknownElement.java:291)
	at jdk.internal.reflect.GeneratedMethodAccessor4.invoke(Unknown Source)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.apache.tools.ant.dispatch.DispatchUtils.execute(DispatchUtils.java:106)
	at org.apache.tools.ant.Task.perform(Task.java:348)
	at org.apache.tools.ant.Target.execute(Target.java:392)
	at org.apache.tools.ant.Target.performTasks(Target.java:413)
	at org.apache.tools.ant.Projec
... (truncated)
```

Classes the defect is known to be located in:

  - com.google.javascript.jscomp.FunctionTypeBuilder
  - com.google.javascript.jscomp.TypedScopeCreator
  - com.google.javascript.rhino.jstype.FunctionBuilder
  - com.google.javascript.rhino.jstype.FunctionType

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.

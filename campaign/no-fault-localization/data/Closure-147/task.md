Repair a real defect in the Java project Closure (Defects4J bug Closure-147).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.CheckGlobalThisTest::testIssue182a
  - com.google.javascript.jscomp.CheckGlobalThisTest::testIssue182b
  - com.google.javascript.jscomp.RuntimeTypeCheckTest::testValueWithInnerFn

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.CheckGlobalThisTest::testIssue182a
junit.framework.AssertionFailedError: There should be one error.  expected:<1> but was:<0>
	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.failNotEquals(Assert.java:329)
	at junit.framework.Assert.assertEquals(Assert.java:78)
	at junit.framework.Assert.assertEquals(Assert.java:234)
	at junit.framework.TestCase.assertEquals(TestCase.java:401)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:832)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:372)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:301)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:270)
	at com.google.javascript.jscomp.CheckGlobalThisTest.testFailure(CheckGlobalThisTest.java:36)
	at com.google.javascript.jscomp.CheckGlobalThisTest.testIssue182a(CheckGlobalThisTest.java:208)
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
--- com.google.javascript.jscomp.CheckGlobalThisTest::testIssue182b
junit.framework.AssertionFailedError: There should be one error.  expected:<1> but was:<0>
	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.failNotEquals(Assert.java:329)
	at junit.framework.Assert.assertEquals(Assert.java:78)
	at junit.framework.Assert.assertEquals(Assert.java:234)
	at junit.framework.TestCase.assertEquals(TestCase.java:401)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:832)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:372)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:301)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:270)
	at com.google.javascript.jscomp.CheckGlobalThisTest.testFailure(CheckGlobalThisTest.java:36)
	at com.google.javascript.jscomp.CheckGlobalThisTest.testIssue182b(CheckGlobalThisTest.java:212)
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
--- com.google.javascript.jscomp.RuntimeTypeCheckTest::testValueWithInnerFn
junit.framework.AssertionFailedError: 
Expected: var jscomp=jscomp||{};jscomp.typecheck=jscomp.typecheck||{};jscomp.typecheck.suspendChecking=false;jscomp.typecheck.log=function(warning$$jscomp_runtimeTypeCheck_0,expr$$jscomp_runtimeTypeCheck_1){};
jscomp.typecheck.checkType=function(expr$$jscomp_runtimeTypeCheck_2,checkers$$jscomp_runtimeTypeCheck_3){if(jscomp.typecheck.suspendChecking)return expr$$jscomp_runtimeTypeCheck_2;jscomp.typecheck.suspendChecking=true;var i$$jscomp_runtimeTypeCheck_4=0;for(;i$$jscomp_runtimeTypeCheck_4<checkers$$jscomp_runtimeTypeCheck_3.length;i$$jscomp_runtimeTypeCheck_4++){var checker$$jscomp_runtimeTypeCheck_5=checkers$$jscomp_runtimeTypeCheck_3[i$$jscomp_runtimeTypeCheck_4];var ok$$jscomp_runtimeTypeCheck_6=
checker$$jscomp_runtimeTypeCheck_5.check(expr$$jscomp_runtimeTypeCheck_2);if(ok$$jscomp_runtimeTypeCheck_6){jscomp.typecheck.suspendChecking=false;return expr$$jscomp_runtimeTypeCheck_2}}var warning$$jscomp_runtimeTypeCheck_7=jscomp.typecheck.prettify_(expr$$jscomp_runtimeTypeCheck_2)+" not in "+checkers$$jscomp_runtimeTypeCheck_3.join(" ");jscomp.typecheck.log(warning$$jscomp_runtimeTypeCheck_7,expr$$jscomp_runtimeTypeCheck_2);jscomp.typecheck.suspendChecking=false;return expr$$jscomp_runtimeTypeCheck_2};
jscomp.typecheck.prettify_=function(expr$$jscomp_runtimeTypeCheck_8){return jscomp.typecheck.getClassName_(expr$$jscomp_runtimeTypeCheck_8)||String(expr$$jscomp_runtimeTypeCheck_8)};
jscomp.typecheck.getClassName_=function(expr$$jscomp_runtimeTypeCheck_9){var className$$jscomp_runtimeTypeCheck_10=void 0;if(typeof expr$$jscomp_runtimeTypeCheck_9=="object"&&expr$$jscomp_runtimeTypeCheck_9&&expr$$jscomp_runtimeTypeCheck_9.constructor){className$$jscomp_runtimeTypeCheck_10=expr$$jscomp_runtimeTypeCheck_9.constructor.name;if(!className$$jscomp_runtimeTypeCheck_10){var funNameRe$$jscomp_runtimeTypeCheck_11=/function (.{1,})\(/;var m$$jscomp_runtimeTypeCheck_12=funNameRe$$jscomp_runtimeTypeCheck_11.exec(expr$$jscomp_runtimeTypeCheck_9.constructor.toString());
className$$jscomp_runtimeTypeCheck_10=m$$jscomp_runtimeTypeCheck_12&&m$$jscomp_runtimeTypeCheck_12.length>1?m$$jscomp_runtimeTypeCheck_12[1]:void 0}}return className$$jscomp_runtimeTypeCheck_10};jscomp.typecheck.Checker=function(){};jscomp.typecheck.Checker.prototype.check=function(expr$$jscomp_runtimeTypeCheck_13){};jscomp.typecheck.ValueChecker_=function(type$$jscomp_runtimeTypeCheck_14){this.type_=type$$jscomp_runtimeTypeCheck_14};
jscomp.typecheck.ValueChecker_.prototype.check=function(expr$$jscomp_runtimeTypeCheck_15){return typeof expr$$jscomp_runtimeTypeCheck_15==this.type_};jscomp.typecheck.ValueChecker_.prototype.toString=function(){return"value("+this.type_+")"};jscomp.typecheck.NullChecker_=function(){};jscomp.typecheck.NullChecker_.prototype.check=function(expr$$jscomp_runtimeTypeCheck_16){return expr$$jscomp_runtimeTypeCheck_16===null};jscomp.typecheck.NullChecker_.prototype.toString=function(){return"value(null)"};
jscomp.typecheck.ExternClassChecker_=function(className$$jscomp_runtimeTypeCheck_17){this.className_=className$$jscomp_runtimeTypeCheck_17};jscomp.typecheck.ExternClassChecker_.windows=[];jscomp.typecheck.ExternClassChecker_.oldOpenFuns=[];
jscomp.typecheck.ExternClassChecker_.trackOpenOnWindow=function(win$$jscomp_runtimeTypeCheck_18){if(win$$jscomp_runtimeTypeCheck_18.tracked)return;win$$jscomp_runtimeTypeCheck_18.tracked=true;var key$$jscomp_runtimeTypeCheck_19=jscomp.typecheck.ExternClassChecker_.oldOpenFuns.length;jscomp.typecheck.ExternClassChecker_.oldOpenFuns.push(win$$jscomp_runtimeTypeCheck_18.open);jscomp.typecheck.ExternClassChecker_.windows.push(win$$jscomp_runtimeTypeCheck_18);win$$jscomp_runtimeTypeCheck_18.open=function(){var w$$jscomp_runtimeTypeCheck_20=
jscomp.typecheck.ExternClassChecker_.oldOpenFuns[key$$jscomp_runtimeTypeCheck_19].apply(this,arguments);jscomp.typecheck.ExternClassChecker_.trackOpenOnWindow(w$$jscomp_runtimeTypeCheck_20);return w$$jscomp_runtimeTypeCheck_20}};jscomp.typecheck.ExternClassChecker_.getGlobalThis_=function(){return function(){return this}.call(null)};
(function(){var globalThis$$jscomp_runtimeTypeCheck_21=jscomp.typecheck.ExternClassChecker_.getGlobalThis_();jscomp.typecheck.ExternClassChecker_.trackOpenOnWindow(globalThis$$jscomp_runtimeTypeCheck_21);var theTop$$jscomp_runtimeTypeCheck_22=globalThis$$jscomp_runtimeTypeCheck_21["top"];if(theTop$$jscomp_runtimeTypeCheck_22)jscomp.typecheck.ExternClassChecker_.trackOpenOnWindow(theTop$$jscomp_runtimeTypeCheck_22)})();
jscomp.typecheck.ExternClassChecker_.prototype.check=function(expr$$jscomp_runtimeTypeCheck_23){var classTypeDefined$$jscomp_runtimeTypeCheck_24=[false];var i$$jscomp_runtimeTypeCheck_25=0;for(;i$$jscomp_runtimeTypeCheck_25<jscomp.typecheck.ExternClassChecker_.windows.length;i$$jscomp_runtimeTypeCheck_25++){var w$$jscomp_runtimeTypeCheck_26=jscomp.typecheck.ExternClassChecker_.windows[i$$jscomp_runtimeTypeCheck_25];if(this.checkWindow_(w$$jscomp_runtimeTypeCheck_26,expr$$jscomp_runtimeTypeCheck_23,
classTypeDefined$$jscomp_runtimeTypeCheck_24))return 
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.

Repair a real defect in the Java project Compress (Defects4J bug Compress-4).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src/main/java
  - test sources       : src/test/java   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - org.apache.commons.compress.archivers.jar.JarArchiveOutputStreamTest::testJarMarker
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testCP437FileRoundtripImplicitUnicodeExtra
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testUtf8FileRoundtripImplicitUnicodeExtra
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testCP437FileRoundtripExplicitUnicodeExtra
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testUtf8FileRoundtripExplicitUnicodeExtra
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testASCIIFileRoundtripImplicitUnicodeExtra
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testUtf8FileRoundtripNoEFSImplicitUnicodeExtra
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testZipArchiveInputStreamReadsUnicodeFields
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testASCIIFileRoundtripExplicitUnicodeExtra
  - org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testUtf8FileRoundtripNoEFSExplicitUnicodeExtra

Failure output from the initial test run:

```
--- org.apache.commons.compress.archivers.jar.JarArchiveOutputStreamTest::testJarMarker
java.io.IOException: central directory is empty, can't expand corrupt archive.
	at org.apache.commons.compress.archivers.zip.ZipFile.populateFromCentralDirectory(ZipFile.java:318)
	at org.apache.commons.compress.archivers.zip.ZipFile.<init>(ZipFile.java:181)
	at org.apache.commons.compress.archivers.zip.ZipFile.<init>(ZipFile.java:158)
	at org.apache.commons.compress.archivers.zip.ZipFile.<init>(ZipFile.java:119)
	at org.apache.commons.compress.archivers.jar.JarArchiveOutputStreamTest.testJarMarker(JarArchiveOutputStreamTest.java:48)
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
--- org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testCP437FileRoundtripImplicitUnicodeExtra
java.io.IOException: central directory is empty, can't expand corrupt archive.
	at org.apache.commons.compress.archivers.zip.ZipFile.populateFromCentralDirectory(ZipFile.java:318)
	at org.apache.commons.compress.archivers.zip.ZipFile.<init>(ZipFile.java:181)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testFile(UTF8ZipFilesTest.java:291)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testFileRoundtrip(UTF8ZipFilesTest.java:202)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testCP437FileRoundtripImplicitUnicodeExtra(UTF8ZipFilesTest.java:75)
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
--- org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testUtf8FileRoundtripImplicitUnicodeExtra
java.io.IOException: central directory is empty, can't expand corrupt archive.
	at org.apache.commons.compress.archivers.zip.ZipFile.populateFromCentralDirectory(ZipFile.java:318)
	at org.apache.commons.compress.archivers.zip.ZipFile.<init>(ZipFile.java:181)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testFile(UTF8ZipFilesTest.java:291)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testFileRoundtrip(UTF8ZipFilesTest.java:202)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testUtf8FileRoundtripImplicitUnicodeExtra(UTF8ZipFilesTest.java:65)
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
--- org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest::testCP437FileRoundtripExplicitUnicodeExtra
java.io.IOException: central directory is empty, can't expand corrupt archive.
	at org.apache.commons.compress.archivers.zip.ZipFile.populateFromCentralDirectory(ZipFile.java:318)
	at org.apache.commons.compress.archivers.zip.ZipFile.<init>(ZipFile.java:181)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testFile(UTF8ZipFilesTest.java:291)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testFileRoundtrip(UTF8ZipFilesTest.java:202)
	at org.apache.commons.compress.archivers.zip.UTF8ZipFilesTest.testCP437FileRoundtripExplicitUnicodeExtra(UTF8ZipFilesTest.java:55)
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
	at org.apache.tools.ant.Targ
... (truncated)
```

Your task: find the root cause and fix it in src/main/java, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.

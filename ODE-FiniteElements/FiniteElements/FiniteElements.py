import matplotlib.pyplot as plt
import numpy as np;
import sympy as smp;
import sys
from PyQt4 import QtCore, QtGui, uic
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

 # Enter file name here.
qtCreatorFile = "Main_form.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self);
        Ui_MainWindow.__init__(self);
        self.setupUi(self);
        self.SetFormInitialValues();

    def AddPlot(self, fig):
        self.canvas = FigureCanvas(fig);
        self.mplvl.addWidget(self.canvas);
        self.canvas.draw();
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True);
        self.mplvl.addWidget(self.toolbar);

    def RemovePlot(self,):
        self.mplvl.removeWidget(self.canvas);
        self.canvas.close();
        self.mplvl.removeWidget(self.toolbar);
        self.toolbar.close();

    def SetFormInitialValues(self):
        self.mplwindow.setStyleSheet("border: 1px solid black");
        self.fig = 0;
        self.A_text.setText("1");
        self.B_text.setText("0");
        self.C_text.setText("-1");
        self.f_text.setText("x");
        self.from_Box.setValue(0);
        self.to_Box.setValue(1);
        self.phi_0_text.setText("2*x");
        self.StringPolynomial_text.setText("(x**i)*(1-x)");
        self.N_spinBox.setValue(3);
        self.GoButton.clicked.connect(self.ProcessForm);
        
    def ProcessForm(self):
        StringResult = "";
        
        # N is the number of partitions
        N = int(self.N_spinBox.value()); 
        # Define the variables
        x = smp.symbols('x');
        A = smp.sympify(str(self.A_text.toPlainText()));
        B = smp.sympify(str(self.B_text.toPlainText()));
        C = smp.sympify(str(self.C_text.toPlainText()));
        f = smp.sympify(str(self.f_text.toPlainText()));

        from_ = self.from_Box.value();
        to_ = self.to_Box.value();

        Coefficients_ = [];
        Equations_ = [];

        # Define phi_0
        phi_0 = str(self.phi_0_text.toPlainText());
        # Define function for phi in each partition node
        StringPolynomial = str(self.StringPolynomial_text.toPlainText());

        ExpressionString = [];
        CoefficientsString = "";

        for i in xrange(1, N + 1):
            CoefficientsString += "c_" + str(i) + " ";
            ExpressionString.append(("c_i * " + StringPolynomial).replace("i", str(i)));

        Coefficients_ = smp.S(CoefficientsString.strip().split());

        # Join the string with a plus character
        ExpressionString = " + ".join(map(str, ExpressionString));

        # Append phi_0 to U(x)
        U = smp.sympify(phi_0) + smp.sympify(ExpressionString);
        U_first_derivative = smp.diff(U, x);
        U_second_derivative = smp.diff(U_first_derivative, x);

        # Define the Residual function R(x)
        R = A * U_second_derivative + B * U_first_derivative + C * U - f;

        StringResult += "Residual function:\n" + str(R) + "\n\n";
        self.console_text.setText(StringResult);

        # Integrals
        for i in xrange(1, N + 1):
            # Set the power
            f = StringPolynomial.replace("i", str(i));
            f = smp.sympify(f);
    
            Integral = smp.integrate(f * R, (x, from_, to_));
            Equations_.append(smp.Eq(Integral, 0));

        # Solve the system of equations
        SolutionVector = smp.solve(Equations_, Coefficients_);

        # Set the coefficients in the U function
        for i in xrange(0, N):
            U = U.subs(Coefficients_[i], SolutionVector[Coefficients_[i]]);

        StringResult += "U function:\n" + str(U) + "\n\n";
        self.console_text.setText(StringResult);

        # this converts thye sympy function into a numpy function
        U = smp.lambdify((x), U, "numpy");

        # Frome here the function U is callable as we are used
        X = np.linspace(from_, to_, num=100);
        Y = U(X);
    
        self.console_text.setText(StringResult);
        
        # Plot the result
        #plt.plot(X, Y);
        #plt.show();
        if self.fig != 0:
            self.RemovePlot();
        
        self.fig = Figure()
        ax1f1 = self.fig.add_subplot(111);
        ax1f1.plot(X, Y);
        self.AddPlot(self.fig);


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv);
    window = MyApp();
    window.show();
    sys.exit(app.exec_());
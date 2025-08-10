'use client';

import { useState } from 'react';
import { toast } from 'sonner';

interface Plan {
  id: string;
  credits: number;
  price: number;
  discount?: string;
  description?: string;
}

const plans: Plan[] = [
  { id: '100', credits: 100, price: 10, description: '100 credits' },
  { id: '500', credits: 500, price: 45, discount: '10% off', description: '500 credits' },
  { id: '1000', credits: 1000, price: 75, discount: '25% off', description: '1000 credits' },
  { id: '5000', credits: 5000, price: 300, discount: '40% off', description: '5000 credits' },
];

export default function BuyCreditsPage() {
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(false);

  const handleBuy = async () => {
    if (!selectedPlan) {
      toast.error('Please select a plan before purchasing.');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/credits/buy`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ planId: selectedPlan.id }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || 'Purchase failed. Please try again.');
      }

      toast.success(`🎉 Successfully purchased ${selectedPlan.credits} credits!`);
      setSelectedPlan(null);

    } catch (error: any) {
      toast.error(`❌ ${error.message || 'Failed to buy credits'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-xl mx-auto p-6 bg-white dark:bg-gray-900 rounded-xl shadow-md my-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Buy Credits</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleBuy();
        }}
        aria-label="Buy credits form"
        className="space-y-5"
      >
        <fieldset className="space-y-4" aria-required="true">
          <legend className="sr-only">Select a credit plan</legend>

          {plans.map((plan) => (
            <label
              key={plan.id}
              htmlFor={`plan-${plan.id}`}
              className={`flex items-center justify-between p-4 border rounded-lg cursor-pointer transition
                ${
                  selectedPlan?.id === plan.id
                    ? 'border-blue-600 bg-blue-50 dark:bg-blue-900'
                    : 'border-gray-300 dark:border-gray-700 hover:border-gray-500 dark:hover:border-gray-500'
                }
              `}
            >
              <div className="flex items-center gap-3">
                <input
                  id={`plan-${plan.id}`}
                  name="credit-plan"
                  type="radio"
                  value={plan.id}
                  checked={selectedPlan?.id === plan.id}
                  onChange={() => setSelectedPlan(plan)}
                  className="w-5 h-5 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-300"
                  required
                />
                <div className="text-gray-900 dark:text-white font-semibold">
                  {plan.description}
                  {plan.discount && (
                    <span className="ml-2 text-green-600 dark:text-green-400 font-normal text-sm">
                      ({plan.discount})
                    </span>
                  )}
                </div>
              </div>
              <div className="text-lg font-bold text-gray-900 dark:text-white">${plan.price}</div>
            </label>
          ))}
        </fieldset>

        <button
          type="submit"
          disabled={!selectedPlan || loading}
          className={`w-full py-3 rounded-lg text-white text-lg font-semibold transition
            ${
              !selectedPlan || loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-black hover:bg-gray-800'
            }
          `}
          aria-busy={loading}
        >
          {loading ? 'Processing...' : 'Buy Credits'}
        </button>
      </form>
    </main>
  );
}
